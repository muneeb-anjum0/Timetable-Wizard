"""
Pretty logging via Rich.
"""
import logging
from rich.logging import RichHandler

def setup_logging(level: int = logging.INFO) -> None:
    root = logging.getLogger()
    if any(isinstance(h, RichHandler) for h in root.handlers):
        return
    for h in list(root.handlers):
        root.removeHandler(h)

    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True, markup=True)],
    )
