import logging
from pathlib import Path

from mychecklist.logging_config import configure_logging


def test_configure_logging_creates_app_log_under_requested_directory(tmp_path: Path) -> None:
    log_directory = tmp_path / "MyChecklist" / "logs"

    log_path = configure_logging(log_directory)

    assert log_path == log_directory / "app.log"
    assert log_path.is_file()
    logging.getLogger("test").info("configuration test")
