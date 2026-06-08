import logging
import sys
from datetime import datetime


def setup_logger(nome: str = "pulsewhales") -> logging.Logger:
    logger = logging.getLogger(nome)
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    fmt = logging.Formatter(
        "[%(asctime)s] %(levelname)-8s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(fmt)
    if not logger.handlers:
        logger.addHandler(handler)
    return logger


LOG = setup_logger()


def banner() -> None:
    print("=" * 60)
    print("  PulseWhales - Fluxo Estrangeiro B3")
    print(f"  {datetime.now():%Y-%m-%d %H:%M:%S}")
    print("=" * 60)
