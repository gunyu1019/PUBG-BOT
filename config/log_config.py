import logging

logging_format = logging.Formatter('[%(asctime)s | %(name)s | %(levelname)s]: %(message)s', "%Y-%m-%d %p %I:%M:%S")


def get_logger(name: str = None):
    _log = logging.getLogger(name)
    _log.setLevel(logging.INFO)
    return _log


log = get_logger()
command = logging.StreamHandler()
command.setFormatter(logging_format)
log.addHandler(command)
