from cryptography.fernet import Fernet
from discord import ApplicationContext
from discord.ext import commands


class GuildConfig(commands.Cog):
    def __init__(self, bot, key):
        self.bot = bot
        self.key = key

    @commands.guild_only()
    @commands.slash_command()
    async def set_classroom(self, ctx: ApplicationContext, secret: str):
        # check if the server is not already registered
        db_query = await self.bot.db.fetch_one(
            "SELECT * FROM servers WHERE ServerID = :server_id",
            {"server_id": ctx.guild.id},
        )

        if db_query is None:
            # add the server
            await self.bot.db.execute(
                """
                INSERT INTO servers (ServerID, ClassroomSecret)
                VALUES (:server_id, :secret)
                """,
                {"server_id": ctx.guild.id, "secret": secret},
            )
        else:
            # update the server
            await self.bot.db.execute(
                """
                UPDATE servers
                SET ClassroomSecret = :secret
                WHERE ServerID = :server_id
                """,
                {"server_id": ctx.guild.id, "secret": secret},
            )

        # TODO: change the respond in future
        await ctx.respond("Classroom set!", ephemeral=True)

    @commands.guild_only()
    @commands.slash_command()
    async def set_password(self, ctx: ApplicationContext, password: str):
        # check if the user is not already registered
        db_query = await self.bot.db.fetch_one(
            """
            SELECT * FROM users
            WHERE UserID = :user_id 
            AND ServerID = :server_id
            """,
            {"user_id": ctx.author.id, "server_id": ctx.guild.id},
        )

        encrypted_password = Fernet(self.key).encrypt(password.encode("utf8"))

        if db_query is None:
            # add the user
            await self.bot.db.execute(
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
            await self.bot.db.execute(
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
