from .logger import logger, info, warning, debug, success, error, critical
from . import launcher


import os

if not os.path.exists(path="sessions"):
    os.mkdir(path="sessions")
