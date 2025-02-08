from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict
import matplotlib.pyplot as plt
import numpy as np


def muted_pastel_colors(n):
    """Generate n distinct muted pastel colors for dark themes."""
    base_colors = plt.cm.Pastel1(np.linspace(0, 1, n))
    return [(r * 0.7, g * 0.7, b * 0.7, 1) for r, g, b, _ in base_colors]

def color_rows_by_group(df):
    """Color rows of a DataFrame based on the 'group' column."""
    # Get unique groups and assign pastel colors
    unique_groups = df["group"].unique()
    color_map = dict(zip(unique_groups, muted_pastel_colors(len(unique_groups))))

    def row_style(row):
        """Style function to color a row based on its group."""
        color = color_map[row["group"]]
        # Convert matplotlib color to CSS format
        color_css = f"background-color: rgba({int(color[0] * 255)}, {int(color[1] * 255)}, {int(color[2] * 255)}, {color[3]})"
        return [color_css] * len(row)

    # Apply the style to the DataFrame
    styled_df = df.style.apply(lambda row: row_style(row), axis=1)
    return styled_df

class AssetType(Enum):
    PARQUET = "parquet"
    CSV = "csv"
    IMAGE = "image"
    JOBLIB_MODEL = "joblib_model"
    CATBOOST_MODEL = "catboost_model"
    OTHER = "other"

    @classmethod
    def from_string(cls, value: str) -> 'AssetType':
        """Convert string to enum value, defaulting to OTHER if not found."""
        try:
            return cls(value.lower())
        except ValueError:
            return cls.OTHER


@dataclass
class AssetMetadata:
    name: str
    group: str
    created_at: datetime
    asset_type: AssetType
    description: str
    custom_metadata: Dict[str, Any]
    relative_path: str
