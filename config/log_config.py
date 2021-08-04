import logging

from utils.directory import directory

logging_format = logging.Formatter('[%(asctime)s | %(name)s | %(levelname)s]: %(message)s', "%Y-%m-%d %p %I:%M:%S")


def get_logger(name: str = None):
    _log = logging.getLogger(name)
    _log.setLevel(logging.INFO)
    return _log


log = get_logger()
command = logging.StreamHandler()
command.setFormatter(logging_format)
log.addHandler(command)

log_event = get_logger("cogs.event.command")
logging_file = logging.FileHandler(f'{directory}/log/command.txt', mode='a', encoding='UTF8')
logging_file.setFormatter(logging_format)
log_event.addHandler(logging_file)

log_event = get_logger("cogs.event.guild")
logging_file = logging.FileHandler(f'{directory}/log/event.txt', mode='a', encoding='UTF8')
logging_file.setFormatter(logging_format)
log_event.addHandler(logging_file)

log_error = get_logger("cogs.error")
logging_file = logging.FileHandler(f'{directory}/log/error.txt', mode='a', encoding='UTF8')
logging_file.setFormatter(logging_format)
log_error.addHandler(logging_file)
