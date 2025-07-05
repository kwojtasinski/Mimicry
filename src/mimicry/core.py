import logging
from pathlib import Path

import yaml

from mimicry.models import SinkConfiguration, TableConfiguration
from mimicry.filesystem import read_text

logger = logging.getLogger(__name__)


def load_table_config(file_path: str | Path) -> TableConfiguration:
    """Load the table configuration from a YAML file.

    Args:
        file_path (str | Path): The path to the YAML file.

    Returns:
        TableConfiguration: The loaded table configuration.

    """
    content = read_text(path=file_path)
    return TableConfiguration(**yaml.safe_load(content))


def load_sink_config(file_path: str | Path) -> SinkConfiguration:
    """Load the sink configuration from a YAML file.

    Args:
        file_path (str | Path): The path to the YAML file.

    Returns:
        SinkConfiguration: The loaded sink configuration.

    """
    content = read_text(path=file_path)
    return SinkConfiguration(**yaml.safe_load(content))
