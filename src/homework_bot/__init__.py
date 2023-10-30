import logging

from .bot import *
from .utils import *

logger = logging.getLogger(__name__)

logger.setLevel(logging.INFO)

handler = logging.StreamHandler()

handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)

logger.addHandler(handler)
