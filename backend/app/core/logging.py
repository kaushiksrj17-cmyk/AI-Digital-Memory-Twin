"""Structured Logging Configuration."""

import logging
import sys
from typing import Dict, Any


def setup_logging():
    """Configure structured console logging for research and memorial tracing."""
    logging_format = (
        "[%(asctime)s] [%(levelname)s] [%(name)s] "
        "[trace_id=%(filename)s:%(lineno)d] %(message)s"
    )

    logging.basicConfig(
        level=logging.INFO,
        format=logging_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

    # Silence noisy third-party loggers if needed
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)


logger = logging.getLogger("echo.memorial")
