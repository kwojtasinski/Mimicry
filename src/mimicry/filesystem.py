from pathlib import Path
from typing import Literal

import boto3
from google.cloud import storage

from mimicry.utils import (
    warn_about_missing_gcs_environment_variables,
    warn_about_missing_s3_environment_variables,
)


def check_path_type(path: str | Path) -> Literal["local", "s3", "gcs"]:
    """Check the type of the path."""
    if isinstance(path, Path):
        return "local"

    if path.startswith("s3://"):
        return "s3"

    if path.startswith("gs://"):
        return "gcs"

    return "local"  # Default to local if no other format matches


def read_text_from_local_path(path: Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def read_text_from_s3(path: str) -> str:
    """Read the contents of a text file from an S3 bucket.
    Args:
        path (str): The S3 path in the format "s3://bucket_name/key".
    Returns:
        str: The content of the file as a string.
    """

    warn_about_missing_s3_environment_variables()

    s3_parts = path.replace("s3://", "").split("/", 1)
    bucket_name = s3_parts[0]
    key = s3_parts[1]

    s3 = boto3.client("s3")

    response = s3.get_object(Bucket=bucket_name, Key=key)

    file_content = response["Body"].read().decode("utf-8")

    return file_content


def read_text_from_gcs(path: str) -> str:
    """
    Read the contents of a text file from a Google Cloud Storage (GCS) bucket.
    Args:
        path (str): The GCS path in the format "gs://bucket_name/path/to/blob".
    Returns:
        str: The content of the file as a string.
    """

    warn_about_missing_gcs_environment_variables()

    storage_client = storage.Client()

    if not path.startswith("gs://"):
        raise ValueError("Invalid GCS path format. It must start with 'gs://'.")

    bucket_name, blob_name = path[5:].split("/", 1)

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    file_content = blob.download_as_text(encoding="utf-8")

    return file_content


def read_text(path: str | Path) -> str:
    """Read the contents of a text file."""

    path_type = check_path_type(path)

    match path_type:
        case "local":
            return read_text_from_local_path(Path(path))
        case "s3":
            return read_text_from_s3(path=path)
        case "gcs":
            return read_text_from_gcs(path=path)
