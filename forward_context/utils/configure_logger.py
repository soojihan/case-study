import logging


def configure_logging(name: str = "statista_context") -> logging.Logger:
    logging.basicConfig(
        level="INFO",
        format="%(asctime)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    return logging.getLogger(name)
