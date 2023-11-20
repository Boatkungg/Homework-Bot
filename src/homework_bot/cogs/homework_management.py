from typing import Optional

from cryptography.fernet import Fernet
from discord import ApplicationContext
from discord.commands import SlashCommandGroup
from discord.ext import commands

from homework_bot import api_operations, db_operations, utils


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
        await ctx.defer()
        if not utils.check_valid_date(assigned) or not utils.check_valid_date(due):
            # TODO: change the respond in future
            await ctx.respond("Invalid assigned or due date!", ephemeral=True)
            return

        db_classroom_query = await db_operations.get_guild(
            self.bot.db, ctx.guild.id
        )

        if db_classroom_query is None:
            # TODO: change the respond in future
            await ctx.respond("You haven't set your classroom yet!")
            return

        classroom_secret = db_classroom_query["ClassroomSecret"]

        db_password_query = await db_operations.get_user_password(
            self.bot.db, ctx.guild.id, ctx.author.id
        )

        if db_password_query is None:
            # TODO: change the respond in future
            await ctx.respond("You haven't set your password yet!")
            return

        password = (
            Fernet(self.key).decrypt(db_password_query["Password"]).decode("utf8")
        )

        json_response, error = await api_operations.add_homework(
            self.bot.http_client,
            self.api_url,
            classroom_secret,
            password,
            api_operations.addHomeworkCriteria(
                subject=subject,
                title=title,
                description=description,
                assigned_date=assigned,
                due_date=due,
                teacher=teacher,
            ),
        )

        if error == "NO_TEACHER":
            # TODO: change the respond in future
            await ctx.respond("You need to specify `teacher` for this homework")
            return

        if error is not None:
            # TODO: change the respond in future
            await ctx.respond("An error occured!")
            return

        # TODO: change the respond in future
        await ctx.respond(
            f"Homework added! ID: {json_response['response']['context']['homework_id']}"
        )

    @commands.guild_only()
    @homework.command()
    async def remove(self, ctx: ApplicationContext, homework_id: int):
        await ctx.defer()
        db_classroom_query = await db_operations.get_guild(
            self.bot.db, ctx.guild.id
        )

        if db_classroom_query is None:
            # TODO: change the respond in future
            await ctx.respond("You haven't set your classroom yet!")
            return

        classroom_secret = db_classroom_query["ClassroomSecret"]

        db_password_query = await db_operations.get_user_password(
            self.bot.db, ctx.guild.id, ctx.author.id
        )

        if db_password_query is None:
            # TODO: change the respond in future
            await ctx.respond("You haven't set your password yet!")
            return

        password = (
            Fernet(self.key).decrypt(db_password_query["Password"]).decode("utf8")
        )

        _, error = await api_operations.remove_homework(
            self.bot.http_client,
            self.api_url,
            classroom_secret,
            password,
            homework_id,
        )

        if error == "HOMEWORK_NOT_FOUND":
            # TODO: change the respond in future
            await ctx.respond("Homework not found!")
            return

        if error is not None:
            # TODO: change the respond in future
            await ctx.respond("An error occured!")
            return

        # TODO: change the respond in future
        await ctx.respond("Homework removed!")
