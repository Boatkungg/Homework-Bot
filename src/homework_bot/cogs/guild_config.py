from cryptography.fernet import Fernet
from discord import ApplicationContext
from discord.commands import SlashCommandGroup
from discord.ext import commands

from homework_bot import db_operations, responses


class GuildConfig(commands.Cog):
    def __init__(self, bot, key):
        self.bot = bot
        self.key = key

    guild = SlashCommandGroup("guild", "Commands for guild")

    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @guild.command(description="Set guild's classroom secret")
    async def secret(self, ctx: ApplicationContext, secret: str):
        await ctx.defer(ephemeral=True)
        # check if the guild is not already registered
        db_query = await db_operations.get_guild(self.bot.db, ctx.guild.id)

        if db_query is None:
            # add the guild
            await db_operations.add_guild(self.bot.db, ctx.guild.id, secret)
        else:
            # update the guild
            await db_operations.update_guild(self.bot.db, ctx.guild.id, secret)

        await responses.normal_response(
            ctx, "**Classroom has been set**", color=self.bot.main_color
        )

    @commands.guild_only()
    @guild.command(description="Set your classroom password")
    async def password(self, ctx: ApplicationContext, password: str):
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

        await responses.normal_response(
            ctx, "**Password has been set**", color=self.bot.main_color
        )

    @secret.error
    async def secret_error(self, ctx: ApplicationContext, error):
        if isinstance(error, commands.MissingPermissions):
            await responses.normal_response(
                ctx,
                "**You don't have permission to use this command**",
                color=self.bot.main_color,
            )
