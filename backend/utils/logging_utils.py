import logging

def setup_logging(level=logging.INFO):
    """
    Set up basic logging configuration for the backend.
    """
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )