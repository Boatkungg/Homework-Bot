from dataclasses import dataclass
from typing import Optional, Literal
import datetime

import discord
from discord import ApplicationContext, Embed, Interaction, ui
from discord.commands import SlashCommandGroup
from discord.ext import commands, tasks

from homework_bot import api_operations, db_operations

timezone = datetime.timezone(datetime.timedelta(hours=7))


class HWNotify(commands.Cog):
    def __init__(self, bot, api_url):
        self.bot = bot
        self.api_url = api_url

    notify = SlashCommandGroup("notify", "Commands for notify")

    @commands.guild_only()
    @notify.command()
    async def set(
        self,
        ctx: ApplicationContext,
        schedule: Literal["disable", "all", "daily", "due"],
    ):
        await ctx.defer()
        db_query = await db_operations.get_notify(
            self.bot.db, ctx.guild.id, ctx.author.id
        )

        if db_query is None:
            await db_operations.add_notify(
                self.bot.db, ctx.guild.id, ctx.author.id, schedule, 3
            )

            await ctx.respond(f"Set notify to {schedule}!", ephemeral=True)

        else:
            await db_operations.update_notify_mode(
                self.bot.db, ctx.guild.id, ctx.author.id, schedule
            )

            await ctx.respond(f"Updated notify to {schedule}!", ephemeral=True)
        

    @commands.guild_only()
    @notify.command()
    async def setting(self, ctx: ApplicationContext, before_due: int):
        await ctx.defer()
        db_query = await db_operations.get_notify(
            self.bot.db, ctx.guild.id, ctx.author.id
        )

        if db_query is None:
            await ctx.respond("You haven't set your notify mode yet!")
            return

        await db_operations.update_notify_before_due(
            self.bot.db, ctx.guild.id, ctx.author.id, before_due
        )

        await ctx.respond(f"Updated notify setting to {before_due}!", ephemeral=True)

    @tasks.loop(time=datetime.time(hour=18, tzinfo=timezone))
    async def send_notify(self):
        """
        Get all servers (guild) then check if there is any user that enabled notify
        Get all notifys mode and before due then make it a list of who need ... days before due
        Enumberate that list and get all homeworks that due in ... days
        Send the homeworks to the user


        TODO: If the user is not in the server anymore, delete the user from the database
        """
        db_classrooms_query = await db_operations.get_classrooms(self.bot.db)

