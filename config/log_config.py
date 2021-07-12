import logging

from utils.directory import directory

log = logging.getLogger()

log.setLevel(logging.INFO)

logging_format = logging.Formatter('[%(asctime)s | %(name)s | %(levelname)s]: %(message)s', "%Y-%m-%d %p %I:%M:%S")
# logging_file = logging.FileHandler(f'{directory}/log/log.txt', mode='a', encoding='UTF8')
# logging_file.setFormatter(logging_format)

command = logging.StreamHandler()
command.setFormatter(logging_format)

log.addHandler(command)
# log.addHandler(logging_file)
