import os
from typing import Optional

import discord
from discord.commands.context import ApplicationContext
from cryptography.fernet import Fernet
from dotenv import load_dotenv

from homework_bot.bot import MainBot


load_dotenv()

key = os.getenv("KEY").encode("utf8")

main_bot = MainBot(
    status=discord.Status.dnd,
    activity=discord.Game("with your homework"),
    intents=discord.Intents.default(),
)


@main_bot.slash_command()
async def ping(ctx: ApplicationContext):
    await ctx.respond(f"Pong! {main_bot.latency * 1000:.2f}ms")


@discord.guild_only()
@main_bot.slash_command()
async def set_classroom(ctx: ApplicationContext, secret: str):
    # check if the server is not already registered
    db_query = await main_bot.db.fetch_one(
        "SELECT * FROM servers WHERE ServerID = :server_id", {"server_id": ctx.guild.id}
    )

    if db_query is None:
        # add the server
        await main_bot.db.execute(
            """
            INSERT INTO servers (ServerID, ClassroomSecret)
            VALUES (:server_id, :secret)
            """,
            {"server_id": ctx.guild.id, "secret": secret},
        )
    else:
        # update the server
        await main_bot.db.execute(
            """
            UPDATE servers
            SET ClassroomSecret = :secret
            WHERE ServerID = :server_id
            """,
            {"server_id": ctx.guild.id, "secret": secret},
        )

    await ctx.respond("Classroom set!")


@main_bot.slash_command()
async def set_password(ctx: ApplicationContext, password: str):
    # check if the user is not already registered
    db_query = await main_bot.db.fetch_one(
        """
        SELECT * FROM users
        WHERE UserID = :user_id 
        AND ServerID = :server_id
        """,
        {"user_id": ctx.author.id, "server_id": ctx.guild.id},
    )

    encrypted_password = Fernet(key).encrypt(password.encode("utf8"))

    if db_query is None:
        # add the user
        await main_bot.db.execute(
            """
            INSERT INTO users (UserID, ServerID, Password)
            VALUES (:user_id, :server_id, :password)
            """,
            {
                "user_id": ctx.author.id,
                "server_id": ctx.guild.id,
                "password": encrypted_password,
            },
        )
    else:
        # update the user
        await main_bot.db.execute(
            """
            UPDATE users
            SET Password = :password
            WHERE UserID = :user_id
            AND ServerID = :server_id
            """,
            {
                "user_id": ctx.author.id,
                "server_id": ctx.guild.id,
                "password": encrypted_password,
            },
        )

    await ctx.respond("Password set!")


@main_bot.slash_group()
async def homework(ctx: ApplicationContext):
    pass


@homework.subcommands()
async def add(
    ctx: ApplicationContext,
    subject: str,
    teacher: Optional[str],
    title: str,
    description: Optional[str],
    assigned: Optional[str],
    due: str,
):
    pass


@homework.subcommands()
async def remove(ctx: ApplicationContext, id: str):
    pass


@homework.subcommands()
async def list(
    ctx: ApplicationContext,
    assigned_before: Optional[str],
    assigned_after: Optional[str],
    due_before: Optional[str],
    due_after: Optional[str],
):
    pass


main_bot.run(os.getenv("TOKEN"))
