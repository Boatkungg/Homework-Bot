from typing import Optional

from cryptography.fernet import Fernet
from discord import ApplicationContext
from discord.commands import SlashCommandGroup
from discord.ext import commands

from homework_bot import utils


class HWManagement(commands.Cog):
    def __init__(self, bot, key, api_url):
        self.bot = bot
        self.key = key
        self.api_url = api_url

    homework = SlashCommandGroup("homework", "Commands for homework")

    @commands.guild_only()
    @homework.command()
    async def add(
        self,
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

        db_classroom_query = await self.bot.db.fetch_one(
            "SELECT * FROM servers WHERE ServerID = :server_id",
            {"server_id": ctx.guild.id},
        )

        if db_classroom_query is None:
            # TODO: change the respond in future
            await ctx.respond("You haven't set your classroom yet!")
            return

        classroom_secret = db_classroom_query["ClassroomSecret"]

        db_password_query = await self.bot.db.fetch_one(
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

        password = (
            Fernet(self.key).decrypt(db_password_query["Password"]).decode("utf8")
        )

        api_response = await self.bot.http_client.post(
            self.api_url + "/api/add_homework",  # TODO: change the url in future
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

        if json_response["response"]["error"] is not None:
            # TODO: change the respond in future
            await ctx.respond("An error occured!")
            return

        # TODO: change the respond in future
        await ctx.respond(
            f"Homework added! ID: {json_response['response']['context']['homework_id']}"
        )

    @commands.guild_only()
    @homework.command()
    async def remove(self, ctx: ApplicationContext, homework_id: str):
        try:
            homework_id = int(homework_id)
        except ValueError:
            # TODO: change the respond in future
            await ctx.respond("Invalid homework ID!")
            return

        db_classroom_query = await self.bot.db.fetch_one(
            "SELECT * FROM servers WHERE ServerID = :server_id",
            {"server_id": ctx.guild.id},
        )

        if db_classroom_query is None:
            # TODO: change the respond in future
            await ctx.respond("You haven't set your classroom yet!")
            return

        classroom_secret = db_classroom_query["ClassroomSecret"]

        db_password_query = await self.bot.db.fetch_one(
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

        password = (
            Fernet(self.key).decrypt(db_password_query["Password"]).decode("utf8")
        )

        api_response = await self.bot.http_client.post(
            self.api_url + "/api/remove_homework",  # TODO: change the url in future
            json={
                "classroom_secret": classroom_secret,
                "classroom_password": password,
                "homework_id": homework_id,
            },
        )

        json_response = api_response.json()

        if json_response["response"]["error"] == "HOMEWORK_NOT_FOUND":
            # TODO: change the respond in future
            await ctx.respond("Homework not found!")
            return

        if json_response["response"]["error"] is not None:
            # TODO: change the respond in future
            await ctx.respond("An error occured!")
            return

        # TODO: change the respond in future
        await ctx.respond("Homework removed!")
