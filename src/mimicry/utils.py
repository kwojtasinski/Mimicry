import logging
import os
from typing import Iterable

logger = logging.getLogger(__name__)


def warn_about_missing_environment_variables(
    *env_vars: Iterable[str], reason: str
) -> None:
    """
    Warn if any of the specified environment variables are not defined.

    Args:
        *env_vars: Variable number of environment variable names to check.
    """
    variables_missing = [var for var in env_vars if var not in os.environ]

    if variables_missing:
        environment_vars_str = ", ".join(variables_missing)
        logger.warning(
            "The following environment variables are not defined: '%s'. %s",
            environment_vars_str,
            reason,
        )


def warn_about_missing_gcs_environment_variables() -> None:
    """
    Warn if the required Google Cloud Storage environment variables are not defined.

    This function checks for the presence of the GOOGLE_APPLICATION_CREDENTIALS
    environment variable, which is necessary for accessing Google Cloud Storage.
    If it is not defined, a warning is logged.

    """
    warn_about_missing_environment_variables(
        "GOOGLE_APPLICATION_CREDENTIALS",
        "GOOGLE_CLOUD_PROJECT",
        reason="To read/write files from/to GCS, Google Cloud credentials must be set in the environment or default credentials will be used.",
    )


def warn_about_missing_s3_environment_variables() -> None:
    """
    Warn if the required AWS environment variables are not defined.

    This function checks for the presence of the AWS_ACCESS_KEY_ID and
    AWS_SECRET_ACCESS_KEY environment variables, which are necessary for
    accessing Amazon S3. If they are not defined, a warning is logged.

    """
    warn_about_missing_environment_variables(
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY",
        reason="To read/write files from/to S3, AWS credentials must be set in the environment or default credentials will be used.",
    )
