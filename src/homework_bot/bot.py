import logging

import databases
import discord
import httpx
from discord import Colour

from homework_bot.utils import pretty_time
from homework_bot.db_operations import create_db

logger = logging.getLogger(__name__)


class MainBot(discord.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.main_color = Colour.from_rgb(185, 153, 146)

        self.http_client = httpx.AsyncClient()
        self.db = databases.Database("sqlite:///database.db")

    async def on_ready(self):
        await self.wait_until_ready()

        logger.info("Logged in as %s", self.user)
        logger.info("ID:   %s", self.user.id)
        logger.info("Ping: %s", pretty_time(self.latency))

        logger.info("-" * 20)
        logger.info("Setting up...")

        await self.db.connect()

        await create_db(self.db)

        logger.info("Ready!")
        logger.info("-" * 20)

    async def close(self):
        logger.info("Closing...")

        await self.http_client.aclose()
        await self.db.disconnect()
        await super().close()
