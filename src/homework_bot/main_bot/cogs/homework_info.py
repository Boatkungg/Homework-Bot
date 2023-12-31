import discord
from cacheout import Cache
from discord import ApplicationContext, Colour, Embed
from discord.ext import commands
from pycord.multicog import add_to_group

from homework_bot import api_operations, db_operations, responses

cache = Cache(maxsize=1000, ttl=300)


class HWInfo(commands.Cog):
    def __init__(self, bot, api_url):
        self.bot = bot
        self.api_url = api_url

    @commands.guild_only()
    @add_to_group("homework")
    @commands.slash_command(description="Get homework info")
    async def info(self, ctx: ApplicationContext, homework_id: int):
        await ctx.defer()
        db_query = await db_operations.get_guild(self.bot.db, ctx.guild.id)

        if db_query is None:
            await responses.normal_response(
                ctx, "**Classroom not set**", color=Colour.red()
            )
            return

        # check if the homework is in cache
        if (db_query["ClassroomSecret"], str(homework_id)) in cache:
            homework = cache.get((db_query["ClassroomSecret"], str(homework_id)))
        else:
            json_response, error = await api_operations.get_homework(
                self.bot.http_client,
                self.api_url,
                db_query["ClassroomSecret"],
                str(homework_id),
            )

            if error is not None:
                await responses.normal_response(
                    ctx,
                    f"**Something went wrong**\nError: `{error}`",
                    color=Colour.red(),
                )
                return

            cache.set(
                (db_query["ClassroomSecret"], str(homework_id)),
                json_response["response"]["context"],
            )
            homework = json_response["response"]["context"]

        embed = Embed(
            title=f"#{homework['homework_id']} • {homework['subject']}",
            timestamp=discord.utils.utcnow(),
            color=self.bot.main_color,
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
