import discord
from discord import ApplicationContext, Embed
from discord.ext import commands

from homework_bot import api_operations, db_operations


class HWInfo(commands.Cog):
    def __init__(self, bot, api_url):
        self.bot = bot
        self.api_url = api_url

    @commands.guild_only()
    @commands.slash_command()
    async def info(self, ctx: ApplicationContext, homework_id: int):
        await ctx.defer()
        db_query = await db_operations.get_guild(self.bot.db, ctx.guild.id)

        if db_query["ClassroomSecret"] is None:
            await ctx.respond("Classroom not set!")
            return

        json_response, error = await api_operations.get_homework(
            self.bot.http_client,
            self.api_url,
            db_query["ClassroomSecret"],
            str(homework_id),
        )

        if error is not None:
            await ctx.respond(error)
            return

        homework = json_response["response"]["context"]

        embed = Embed(
            title=f"#{homework['homework_id']} • {homework['subject']}",
            timestamp=discord.utils.utcnow(),
        )

        description = "```\n"
        description += f"{homework['title']}\n"
        description += (
            f"{homework['description']}\n\n" if homework["description"] else "\n"
        )
        description += f"Teacher: {homework['teacher']}\n"
        description += f"Assigned: {homework['assigned_date']}\n"
        description += f"Due: {homework['due_date']}\n"
        description += "```"

        embed.description = description

        await ctx.respond(embed=embed, ephemeral=True)
