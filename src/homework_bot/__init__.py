import logging

from .api_operations import *
from .bot import *
from .cogs import *
from .db_operations import *
from .responses import *
from .utils import *

logger = logging.getLogger(__name__)

logger.setLevel(logging.INFO)

handler = logging.StreamHandler()

handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)

logger.addHandler(handler)
