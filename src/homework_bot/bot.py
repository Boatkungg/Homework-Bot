import logging

import databases
import discord
import httpx

logger = logging.getLogger(__name__)


class MainBot(discord.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.http_client = httpx.AsyncClient()
        self.db = databases.Database("sqlite:///database.db")

    async def on_ready(self):
        logger.info(f"Logged in as {self.user}")
        logger.info(f"ID:   {self.user.id}")
        logger.info(f"Ping: {float(self.latency * 1000):.2}ms")

        logger.info("-" * 20)
        logger.info("Setting up...")

        await self.db.connect()

        await self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS servers (
            ServerID BIGINT PRIMARY KEY,
            ClassroomSecret TEXT
            )
            """
        )

        await self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
            UserID BIGINT PRIMARY KEY,
            ServerID BIGINT,
            Password TEXT
            )
            """
        )

        logger.info("Ready!")
        logger.info("-" * 20)

    async def close(self):
        await self.http_client.aclose()
        await self.db.disconnect()
        await super().close()
