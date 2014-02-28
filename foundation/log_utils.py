# python imports
import os
import sys
import logging
import platform

version = platform.python_version_tuple()
if version[1] == 6:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass
else:
    from logging import NullHandler

def setup_root_logger(level=logging.DEBUG, formatter=None, log_file=None,
                log_size=5242880, log_count=5):
    logger = logging.getLogger()
    logger.setLevel(level)
    if formatter is None:
        formatter = '"%(asctime)s - %(levelname)s - %(name)s - %(message)s"'
    formatter = logging.Formatter(formatter)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.addHandler(NullHandler())

    if log_file:
        log_dir = os.path.dirname(log_file)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        rotating_handler = logging.handlers.RotatingFileHandler(
            filename=log_file,
            maxBytes=log_size,
            backupCount=log_count
        )
        rotating_handler.setFormatter(formatter)
        logger.addHandler(rotating_handler)

    return logger
