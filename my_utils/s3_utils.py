
def modify_yaml_in_s3(bucket_name, key, modify_function):
    """
    Reads a YAML file from S3, modifies it, and writes it back to the same location.

    Args:
        bucket_name (str): Name of the S3 bucket.
        key (str): Path to the YAML file in the bucket.
        modify_function (function): A function that takes a dictionary and modifies it in place.
    """
    try:
        import boto3
        import yaml
        from botocore.exceptions import NoCredentialsError, PartialCredentialsError
    except ImportError as e:
        raise ImportError(
            "This function requires the boto3 and PyYAML libraries."
        ) from e

    s3 = boto3.client('s3')

    try:
        # Download the YAML file from S3
        response = s3.get_object(Bucket=bucket_name, Key=key)
        yaml_content = response['Body'].read().decode('utf-8')

        # Parse the YAML content
        yaml_data = yaml.safe_load(yaml_content)

        # Modify the YAML data
        modify_function(yaml_data)

        # Serialize the modified YAML back to a string
        modified_yaml_content = yaml.dump(yaml_data, default_flow_style=False)

        # Upload the modified YAML back to S3
        s3.put_object(Bucket=bucket_name, Key=key, Body=modified_yaml_content)
        print(f"Successfully modified and re-saved {key} in bucket {bucket_name}.")

    except NoCredentialsError:
        print("No AWS credentials found.")
    except PartialCredentialsError:
        print("Incomplete AWS credentials.")
    except Exception as e:
        print(f"An error occurred: {e}")



def traverse_s3_paths(root_path, num_levels=3):
    """
    Traverses S3 paths starting from root_path, going num_levels levels deep into each folder and
    returns a list of paths that are exactly 3 levels deeper than each root folder.
    This is good for getting the paths of models under a certain flurry, will only work if there is only
    one experiment under each model.
    Assumes single folder at each level but may contain other files.

    Args:
        root_path (str): S3 path in format 'bucket/prefix'

    Returns:
        list: List of paths that are exactly 3 levels deeper than each root folder
    """
    try:
        import boto3
        from botocore.exceptions import ClientError
    except ImportError as e:
        raise ImportError(
            "This function requires the boto3 library."
        ) from e

    # Split bucket and prefix
    bucket_name = root_path.split('/')[0]
    prefix = '/'.join(root_path.split('/')[1:])
    if not prefix.endswith('/'):
        prefix += '/'

    s3_client = boto3.client('s3')
    result_paths = []

    try:
        # List all objects with the given prefix
        paginator = s3_client.get_paginator('list_objects_v2')
        response_iterator = paginator.paginate(
                Bucket=bucket_name,
                Prefix=prefix,
                Delimiter='/'
        )

        # Get root level folders
        for response in response_iterator:
            if 'CommonPrefixes' in response:
                root_folders = [p['Prefix'] for p in response['CommonPrefixes']]
                # For each root folder, traverse 3 levels deep
                for folder in root_folders:
                    print(folder)
                    current_path = folder
                    level = 0

                    # Go 3 levels deep
                    while level < num_levels:
                        # List objects in current path
                        sub_response = s3_client.list_objects_v2(
                                Bucket=bucket_name,
                                Prefix=current_path,
                                Delimiter='/'
                        )

                        if 'CommonPrefixes' not in sub_response:
                            # No more folders found
                            break

                        # Take the first folder found
                        current_path = sub_response['CommonPrefixes'][0]['Prefix']
                        level += 1
                    # Only add paths that went exactly 3 levels deep
                    if level == num_levels:
                        result_paths.append(f"s3://{bucket_name}/{current_path}")

        return result_paths

    except ClientError as e:
        print(f"Error accessing S3: {e}")
        return []
