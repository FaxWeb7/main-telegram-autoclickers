import sys
from loguru import logger

logger.remove()
logger.add(sink=sys.stdout, format="<level>{message}</level>", encoding=sys.stdout.encoding)
logger = logger.opt(colors=True)