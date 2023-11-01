import logging

from .bot import *
from .utils import *
from .cogs import *
from .db_operations import *
from .api_operations import *

logger = logging.getLogger(__name__)

logger.setLevel(logging.INFO)

handler = logging.StreamHandler()

handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)

logger.addHandler(handler)
