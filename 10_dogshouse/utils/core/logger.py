import sys
import re
import requests
from loguru import logger
from data import config

TELEGRAM_API_URL = f"https://api.telegram.org/bot{config.BOT_TOKEN}/sendMessage"
def formatter(record, format_string):
    return format_string + record["extra"].get("end", "\n") + "{exception}"

def clean_brackets(raw_str):
    return re.sub(r'<.*?>', '', raw_str)

def send_log_to_telegram(message):
    try:
        response = requests.post(TELEGRAM_API_URL, data={'chat_id': config.CHAT_ID, 'text': message})
        if response.status_code != 200:
            logger.error(f"Failed to send log to Telegram: {response.text}")
    except Exception as e:
        logger.error(f"Failed to send log to Telegram: {e}")

def logging_setup():
    format_info = "<green>{time:HH:mm:ss.SS}</green> | <blue>{level}</blue> | <level>{message}</level>"
    format_error = "<green>{time:HH:mm:ss.SS}</green> | <blue>{level}</blue> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>"
    logger_path = r"logs/out.log"

    logger.remove()

    logger.add(logger_path, colorize=True, format=lambda record: formatter(record, clean_brackets(format_error)))
    logger.add(sys.stdout, colorize=True, format=lambda record: formatter(record, format_info), level="INFO")
    if config.USE_TG_BOT:
        logger.add(lambda msg: send_log_to_telegram(msg), format="{time:HH:mm:ss.SS} | {level} | {message}", level="INFO")


logging_setup()
