import sys
import re
from loguru import logger


def formatter(record, format_string):
    return format_string + record["extra"].get("end", "\n") + "{exception}"


def clean_brackets(raw_str):
    return re.sub(r'<.*?>', '', raw_str)


def logging_setup():
    format_info = "<green>{time:HH:mm:ss.SS}</green> | <blue>{level}</blue> | <level>{message}</level>"
    format_error = "<green>{time:HH:mm:ss.SS}</green> | <blue>{level}</blue> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>"
    logger_path = r"logs/out.log"

    logger.remove()

    logger.add(logger_path, colorize=True, format=lambda record: formatter(record, clean_brackets(format_error)))
    logger.add(sys.stdout, colorize=True, format=lambda record: formatter(record, format_info), level="INFO")


logging_setup()
