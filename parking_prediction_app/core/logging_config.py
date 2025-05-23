import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler


def setup_logging(log_dir: Path = Path("logs"), level: int = logging.INFO) -> logging.Logger:
    """
    Configure logging for the application.

    Args:
        log_dir: Directory to store log files
        level: Logging level

    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    log_dir.mkdir(exist_ok=True, parents=True)

    # Create logger
    logger = logging.getLogger("parking_prediction")
    logger.setLevel(level)

    # Create formatters
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_formatter = logging.Formatter(
        "%(levelname)s: %(message)s"
    )

    # Create handlers
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(level)

    file_handler = RotatingFileHandler(
        log_dir / "app.log",
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(level)

    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger