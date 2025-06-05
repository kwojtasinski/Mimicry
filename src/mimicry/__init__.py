import logging
import os


def setup_logging() -> None:
    logger = logging.getLogger("mimicry")
    log_level = logging.DEBUG if os.getenv("MIMICRY_DEBUG") else logging.INFO
    logger.setLevel(log_level)
    handler = logging.StreamHandler()
    handler.setLevel(log_level)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)


setup_logging()
