import sys
from threading import Thread
from loguru import logger

logger.remove()
logger.add(sink=sys.stdout, format="<level>{message}</level>")

logger = logger.opt(colors=True)
