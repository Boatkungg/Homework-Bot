import os
from typing import Optional, Union

import discord
from discord import ApplicationContext
from cryptography.fernet import Fernet
from dotenv import load_dotenv

from homework_bot.bot import MainBot
from homework_bot import utils


load_dotenv()

API_URL = "http://localhost:5000"

key = os.getenv("KEY").encode("utf8")

main_bot = MainBot(
    status=discord.Status.dnd,
    activity=discord.Game("with your homework"),
    intents=discord.Intents.default(),
    debug_guilds=[856028294645153802],
)


@main_bot.slash_command()
async def ping(ctx: ApplicationContext):
    # TODO: change the respond in future
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

    # TODO: change the respond in future
    await ctx.respond("Classroom set!", ephemeral=True)


@discord.guild_only()
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

    # TODO: change the respond in future
    await ctx.respond("Password set!", ephemeral=True)


homework = main_bot.create_group("homework", "Commands for homework")


@discord.guild_only()
@homework.command()
async def add(
    ctx: ApplicationContext,
    subject: str,
    title: str,
    due: str,
    teacher: Optional[str],
    description: Optional[str],
    assigned: Optional[str],
):
    if not utils.check_valid_date(assigned) or not utils.check_valid_date(due):
        # TODO: change the respond in future
        await ctx.respond("Invalid assigned or due date!")
        return

    db_classroom_query = await main_bot.db.fetch_one(
        "SELECT * FROM servers WHERE ServerID = :server_id",
        {"server_id": ctx.guild.id},
    )

    if db_classroom_query is None:
        # TODO: change the respond in future
        await ctx.respond("You haven't set your classroom yet!")
        return

    classroom_secret = db_classroom_query["ClassroomSecret"]

    db_password_query = await main_bot.db.fetch_one(
        """
        SELECT * FROM users
        WHERE UserID = :user_id 
        AND ServerID = :server_id
        """,
        {"user_id": ctx.author.id, "server_id": ctx.guild.id},
    )

    if db_password_query is None:
        # TODO: change the respond in future
        await ctx.respond("You haven't set your password yet!")
        return

    password = Fernet(key).decrypt(db_password_query["Password"]).decode("utf8")

    api_response = await main_bot.http_client.post(
        API_URL + "/api/add_homework",
        json={
            "classroom_secret": classroom_secret,
            "classroom_password": password,
            "subject": subject,
            "teacher": teacher,
            "title": title,
            "description": description,
            "assigned_date": assigned,
            "due_date": due,
        },
    )

    json_response = api_response.json()

    if json_response["response"]["error"] == "NO_TEACHER":
        # TODO: change the respond in future
        await ctx.respond("You need to specify `teacher` for this homework")
        return

    # TODO: change the respond in future
    await ctx.respond(
        f"Homework added! ID: {json_response['response']['context']['homework_id']}"
    )


@homework.command()
async def remove(ctx: ApplicationContext, id: str):
    pass


@homework.command()
async def list(
    ctx: ApplicationContext,
    assigned_before: Optional[str],
    assigned_after: Optional[str],
    due_before: Optional[str],
    due_after: Optional[str],
):
    pass


main_bot.run(os.getenv("TOKEN"))
