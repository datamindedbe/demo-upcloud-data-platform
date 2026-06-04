import logging
import multiprocessing
import os
import sys

# Expose only the interesting method
from canal.stream_operators.grouped_within import grouped_within
from canal.sink import *
from canal.source import *
from canal.flow import *


logging.basicConfig(
    stream=sys.stderr,
    format=os.getenv("CANAL_LOGGING_FORMAT", "%(message)s"),
    level=os.getenv("CANAL_LOGGING_LEVEL", "INFO"),
)
logger = logging.getLogger()

# Current canal code is not working with the spawn method, hence we force fork
multiprocessing.set_start_method("fork", force=True)
