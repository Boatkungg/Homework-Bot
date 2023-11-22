from cryptography.fernet import Fernet
from discord import ApplicationContext
from discord.ext import commands

from homework_bot import db_operations, responses


class GuildConfig(commands.Cog):
    def __init__(self, bot, key):
        self.bot = bot
        self.key = key

    @commands.guild_only()
    @commands.slash_command()
    async def set_classroom(self, ctx: ApplicationContext, secret: str):
        await ctx.defer()
        # check if the server is not already registered
        db_query = await db_operations.get_guild(self.bot.db, ctx.guild.id)

        if db_query is None:
            # add the server
            await db_operations.add_guild(self.bot.db, ctx.guild.id, secret)
        else:
            # update the server
            await db_operations.update_guild(self.bot.db, ctx.guild.id, secret)

        # TODO: change the respond in future
        await responses.normal_response(
            ctx, "**Classroom has been set!**", color=self.bot.main_color
        )

    @commands.guild_only()
    @commands.slash_command()
    async def set_password(self, ctx: ApplicationContext, password: str):
        await ctx.defer(ephemeral=True)
        # check if the user is not already registered
        db_query = await db_operations.get_user_password(
            self.bot.db, ctx.guild.id, ctx.author.id
        )

        encrypted_password = Fernet(self.key).encrypt(password.encode("utf8"))

        if db_query is None:
            # add the user
            await db_operations.add_user(
                self.bot.db, ctx.guild.id, ctx.author.id, encrypted_password
            )
        else:
            # update the user
            await db_operations.update_user(
                self.bot.db, ctx.guild.id, ctx.author.id, encrypted_password
            )

        # TODO: change the respond in future
        await responses.normal_response(
            ctx, "**Password has been set!**", color=self.bot.main_color
        )
