from discord import ApplicationContext, Colour
from discord.commands import SlashCommandGroup
from discord.ext import commands

from homework_bot import api_operations, responses


class U_CRManagement(commands.Cog):
    def __init__(self, bot, api_url):
        self.bot = bot
        self.api_url = api_url

    classroom = SlashCommandGroup("classroom", "Commands for classroom")

    @classroom.command(description="Create new classroom")
    @commands.is_owner()
    async def new(self, ctx: ApplicationContext, name: str, password: str):
        await ctx.defer(ephemeral=True)
        json_response, error = await api_operations.new_classroom(
            self.bot.http_client, self.api_url, name, password
        )

        if error is not None:
            await responses.normal_response(
                ctx,
                f"**Something went wrong**\nError: `{error}`",
                color=Colour.red(),
            )
            return

        await responses.normal_response(
            ctx,
            f"**Classroom created**\nClassroom secret: `{json_response['response']['context']['classroom_secret']}`",
            color=self.bot.main_color,
        )

    @new.error
    async def new_error(self, ctx: ApplicationContext, error):
        if isinstance(error, commands.NotOwner):
            await responses.normal_response(
                ctx,
                "**You don't have permission to use this command**",
                color=Colour.red(),
            )
            return
            
