from dataclasses import asdict
from datetime import datetime
from pathlib import Path
import json
import os
import shutil
import pandas as pd
from typing import Dict, Any, Optional

from my_utils.asset_man.asset_man_helpers import AssetMetadata, AssetType, color_rows_by_group


def get_settings() -> Dict[str, Any]:
    """Get the current settings."""
    current_dir = os.path.dirname(__file__)
    settings_fpath = os.path.join(current_dir, "asset_man_settings.json")
    with open(settings_fpath, 'r') as f:
        return json.load(f)

# Global settings
_settings = {'root_path': get_settings()['assets_root']}


def _get_root_path() -> Path:
    """Get the current root path."""
    return Path(_settings['root_path'])


def _get_metadata_file() -> Path:
    """Get the path to the metadata file."""
    return _get_root_path() / "metadata.json"


def _initialize_storage():
    """Create the root directory and metadata file if they don't exist."""
    root_path = _get_root_path()
    metadata_file = _get_metadata_file()

    root_path.mkdir(parents=True, exist_ok=True)
    if not metadata_file.exists():
        _save_metadata({})


def _load_metadata() -> Dict[str, Dict]:
    """Load the metadata from the JSON file."""
    metadata_file = _get_metadata_file()
    if metadata_file.exists():
        with open(metadata_file, 'r') as f:
            data = json.load(f)
            # Convert string dates back to datetime objects and asset types to enum
            for asset_data in data.values():
                asset_data['created_at'] = datetime.fromisoformat(asset_data['created_at'])
                asset_data['asset_type'] = AssetType.from_string(asset_data['asset_type'])
            return data
    return {}


def _save_metadata(metadata: Dict[str, Dict]):
    """Save the metadata to the JSON file."""
    # Convert datetime objects to ISO format strings and enum to string for JSON serialization
    serializable_metadata = {}
    for asset_name, asset_data in metadata.items():
        serializable_metadata[asset_name] = {
            **asset_data,
            'created_at': asset_data['created_at'].isoformat(),
            'asset_type': asset_data['asset_type'].value if isinstance(asset_data['asset_type'], AssetType) else
                          asset_data['asset_type']
        }

    with open(_get_metadata_file(), 'w') as f:
        json.dump(serializable_metadata, f, indent=4)


def save_asset(
        asset_data: Any,
        name: str,
        asset_type: Optional[AssetType] = None,
        description: str = "",
        group: str = None,
        custom_metadata: Dict[str, Any] = None,
        save_function: callable = None
):
    """
    Save an asset with its metadata.

    Args:
        asset_data: The actual asset to save
        name: Name of the asset
        asset_type: Type of the asset (either AssetType enum or string)
        description: Optional description of the asset
        group: Optional group (folder) to save the asset in
        custom_metadata: Optional dictionary of custom metadata
        save_function: Optional custom function to save the asset
    """
    _initialize_storage()
    metadata = _load_metadata()

    # Convert string asset_type to enum if necessary
    if isinstance(asset_type, str):
        asset_type = AssetType.from_string(asset_type)

    if asset_type is None:
       if hasattr(asset_data, 'to_parquet'):
          asset_type = AssetType.PARQUET
       elif hasattr(asset_data, 'to_csv'):
            asset_type = AssetType.CSV
       elif hasattr(asset_data, 'save_model'):
            asset_type = AssetType.CATBOOST_MODEL

    # Determine the save path
    relative_path = name
    if group:
        group_path = _get_root_path() / group
        group_path.mkdir(exist_ok=True)
        relative_path = f"{group}/{name}"

    save_path = _get_root_path() / relative_path

    # Save the asset using the appropriate method
    if save_function:
        save_function(asset_data, save_path)
    elif asset_type == AssetType.PARQUET:
        if hasattr(asset_data, 'to_parquet'):
            asset_data.to_parquet(save_path)
    elif asset_type == AssetType.CSV:
        if hasattr(asset_data, 'to_csv'):
            asset_data.to_csv(save_path)
    elif asset_type == AssetType.JOBLIB_MODEL:
        import joblib
        joblib.dump(asset_data, save_path)
    elif asset_type == AssetType.CATBOOST_MODEL:
        # Save CatBoost model - will raise error if model is not a CatBoost model
        save_path = str(save_path)  # CatBoost expects string path
        if not save_path.endswith('.cbm'):
            save_path += '.cbm'
        asset_data.save_model(save_path)
    else:
        raise ValueError('Unknown file type')

    # Save metadata
    asset_metadata = AssetMetadata(
            name=name,
            group=group,
            created_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            asset_type=asset_type,
            description=description,
            custom_metadata=custom_metadata or {},
            relative_path=relative_path
    )

    metadata[f'{group}_{name}'] = asdict(asset_metadata)
    _save_metadata(metadata)


def load_asset(name: str, group: Optional[str], load_function: callable = None) -> Any:
    """Load an asset by name."""
    _initialize_storage()
    metadata = _load_metadata()
    if group:
        name = f"{group}_{name}"

    if name not in metadata:
        raise ValueError(f"Asset '{name}' not found")

    asset_data = metadata[name]
    file_path = _get_root_path() / asset_data['relative_path']

    if load_function:
        return load_function(file_path)

    # Default loading behavior based on asset_type
    asset_type = asset_data['asset_type']
    if asset_type == AssetType.PARQUET:
        return pd.read_parquet(file_path)
    elif asset_type == AssetType.CSV:
        return pd.read_csv(file_path)
    elif asset_type == AssetType.JOBLIB_MODEL:
        import joblib
        return joblib.load(file_path)
    elif asset_type == AssetType.CATBOOST_MODEL:
        from catboost import CatBoostRegressor, CatBoostClassifier
        # Try loading as both regressor and classifier
        try:
            model = CatBoostRegressor()
            model.load_model(str(file_path))
            return model
        except:
            try:
                model = CatBoostClassifier()
                model.load_model(str(file_path))
                return model
            except:
                raise ValueError("Failed to load CatBoost model")
    else:
        # For unknown types, return bytes
        with open(file_path, 'rb') as f:
            return f.read()


def list_assets(group_name: Optional[str]) -> pd.DataFrame:
    """Display all assets in a formatted table."""
    _initialize_storage()
    sync_metadata()
    metadata = _load_metadata()
    if not metadata:
        return pd.DataFrame(columns=['group', 'name', 'created_at', 'asset_type',
                                     'description', 'relative_path', 'custom_metadata'])

    # Convert metadata to a list of dictionaries
    assets_list = []
    for name, data in metadata.items():
        asset_dict = {
            'group':         data['group'],
            'name':          name.removeprefix(f"{data['group']}_"),
            'created_at':    data['created_at'],
            'asset_type':    data['asset_type'].value,
            'description':   data['description'],
            'relative_path': data['relative_path']
        }
        # Add custom metadata as separate columns
        for key, value in data['custom_metadata'].items():
            asset_dict[f'custom_{key}'] = value
        assets_list.append(asset_dict)

    if group_name:
        assets_list = [asset for asset in assets_list if asset['group'] == group_name]

    return color_rows_by_group(pd.DataFrame(assets_list).sort_values(['group', 'name']))


def update_metadata(name: str, **kwargs):
    """Update metadata for an existing asset."""
    _initialize_storage()
    metadata = _load_metadata()
    if name not in metadata:
        raise ValueError(f"Asset '{name}' not found")

    # Update only the provided fields
    for key, value in kwargs.items():
        if key in metadata[name]:
            # Convert asset_type string to enum if necessary
            if key == 'asset_type' and isinstance(value, str):
                value = AssetType.from_string(value)
            metadata[name][key] = value
        elif key == 'custom_metadata':
            metadata[name]['custom_metadata'].update(value)

    _save_metadata(metadata)


def create_group(group_name: str):
    """Create a new asset group (folder)."""
    _initialize_storage()
    group_path = _get_root_path() / group_name
    if group_path.exists():
        raise ValueError(f"Group '{group_name}' already exists")
    group_path.mkdir(parents=True)


def remove_group(group_name: str):
    """Remove an asset group if it's empty."""
    _initialize_storage()
    group_path = _get_root_path() / group_name
    if not group_path.exists():
        raise ValueError(f"Group '{group_name}' does not exist")

    if any(group_path.iterdir()):
        raise ValueError(f"Group '{group_name}' is not empty")

    group_path.rmdir()

def sync_metadata():
    """ Synchronize metadata and delete assets from metadata that no longer exist"""
    _initialize_storage()
    metadata = _load_metadata()
    metadata_copy = metadata.copy()
    for name, data in metadata_copy.items():
        file_path = _get_root_path() / data['relative_path']
        if not file_path.exists():
            del metadata[name]
    _save_metadata(metadata)

def delete_asset(name: str):
    """Delete an asset by name."""
    _initialize_storage()
    metadata = _load_metadata()
    if name not in metadata:
        raise ValueError(f"Asset '{name}' not found")

    # Delete the asset file
    file_path = _get_root_path() / metadata[name]['relative_path']
    if file_path.exists():
        file_path.unlink()

    # Delete the metadata entry
    del metadata[name]
    _save_metadata(metadata)

def update_settings(new_root_path: str):
    """Update the root path and migrate existing assets."""
    _initialize_storage()
    old_root = _get_root_path()
    new_root = Path(new_root_path)

    if old_root == new_root:
        return

    # Create new directory
    new_root.mkdir(parents=True, exist_ok=True)

    # Copy all files and directories
    for item in old_root.glob('*'):
        if item.is_file():
            shutil.copy2(item, new_root)
        else:
            shutil.copytree(item, new_root / item.name)

    # Update root path
    _settings['root_path'] = new_root


def list_groups():
    """List all asset groups."""
    _initialize_storage()
    return [item.name for item in _get_root_path().iterdir() if item.is_dir()]
