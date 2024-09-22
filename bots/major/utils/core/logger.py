import sys
from loguru import logger

logger.remove()
logger.add(sink=sys.stdout, format="{level: <8} | <level>{message}</level>")
logger = logger.opt(colors=True)