import datetime
import logging
from typing import List

import discord
from discord import ApplicationContext, Embed, Option
from discord.commands import SlashCommandGroup
from discord.ext import commands, tasks

from homework_bot import api_operations, db_operations

logger = logging.getLogger(__name__)

timezone_delta = datetime.timedelta(hours=7)
timezone = datetime.timezone(timezone_delta)


def get_notify(db_notifies_query):
    notifies_daily = []
    notifies_due = {}

    for notify in db_notifies_query:
        mode = notify["Mode"]
        user_id = notify["UserID"]
        before_due = str(notify["BeforeDue"])

        if mode in ["all", "daily"]:
            notifies_daily.append(user_id)

        if mode in ["all", "due"]:
            if before_due not in notifies_due:
                notifies_due[before_due] = []

            notifies_due[before_due].append(user_id)

    return notifies_daily, notifies_due


async def get_homeworks(
    http_client,
    api_url,
    classroom_secret,
    criteria: api_operations.listHomeworksCriteria,
):
    api_response, error = await api_operations.list_homeworks(
        http_client,
        api_url,
        classroom_secret,
        criteria=criteria,
    )

    if error is not None:
        logger.error(f"An error occured when listing homeworks: {error}")
        return None

    daily_homeworks = [
        {
            "homework_id": homework["homework_id"],
            "subject": homework["subject"],
            "assigned_date": homework["assigned_date"],
            "due_date": homework["due_date"],
        }
        for homework in api_response["response"]["context"]["homeworks"]
    ]

    return daily_homeworks, api_response["response"]["context"]["max_page"]


def make_embed(homeworks: List[dict], title: str, color, message: str = None):
    embed = Embed(
        title=title,
        timestamp=discord.utils.utcnow(),
        color=color,
    )

    description = "```\n"
    for homework in homeworks:
        description += f"#{homework['homework_id']} • {homework['subject']}\n"
        description += (
            f"Assigned: {homework['assigned_date']} • Due: {homework['due_date']}\n"
        )
        description += "---\n"

    if message is not None:
        description += f"{message}\n"

    description += "```"

    embed.description = description

    return embed


def make_no_homework_embed(title: str, color):
    embed = Embed(
        title=title,
        timestamp=discord.utils.utcnow(),
        color=color,
    )

    embed.set_footer(text="No homework yay!")

    return embed


def make_homework_embed(
    homeworks: List[dict], title: str, pages: int = None, color=Embed.Empty
):
    if len(homeworks) == 0:
        return make_no_homework_embed(title, color)

    return make_embed(homeworks, title, color, ("more..." if pages > 1 else None))


async def send_notifications(bot, users, embed):
    for user_id in users:
        user = await bot.fetch_user(user_id)
        if user is None:
            continue

        try:
            await user.send(embed=embed)
        except discord.Forbidden:
            logging.error(f"Failed to send homeworks to {user_id}")


class HWNotify(commands.Cog):
    def __init__(self, bot, api_url):
        self.bot = bot
        self.api_url = api_url
        self.send_notify.start()  # pylint: disable=no-member

    notify = SlashCommandGroup("notify", "Commands for notify")

    @notify.command()
    async def set(
        self,
        ctx: ApplicationContext,
        schedule: Option(
            str, choices=["disable", "all", "daily", "due"], required=True
        ),
    ):
        await ctx.defer(ephemeral=True)
        db_query = await db_operations.get_notify(
            self.bot.db, ctx.guild.id, ctx.author.id
        )

        if db_query is None:
            await db_operations.add_notify(
                self.bot.db, ctx.guild.id, ctx.author.id, schedule, 3
            )

            await ctx.respond(f"Set notify to {schedule}!")

        else:
            await db_operations.update_notify_mode(
                self.bot.db, ctx.guild.id, ctx.author.id, schedule
            )

            await ctx.respond(f"Updated notify to {schedule}!")

    @commands.guild_only()
    @notify.command()
    async def setting(self, ctx: ApplicationContext, before_due: int):
        await ctx.defer(ephemeral=True)
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
        logging.info("Sending daily notify...")
        bot_guilds = [guild.id for guild in self.bot.guilds]

        db_guilds_query = await db_operations.get_all_guilds(self.bot.db)
        db_guilds_query = [
            {g["GuildID"]: g["ClassroomSecret"]}
            for g in db_guilds_query
            if g["GuildID"] in bot_guilds
        ]

        for guild in db_guilds_query:
            guild_id = list(guild.keys())[0]
            classroom_secret = list(guild.values())[0]

            db_notifies_query = await db_operations.get_all_notifies(
                self.bot.db, guild_id
            )

            if db_notifies_query is None:
                continue

            notifies_daily, notifies_due = get_notify(db_notifies_query)

            today_date = (datetime.datetime.utcnow() + timezone_delta).strftime(
                "%Y-%m-%d"
            )
            daily_homeworks, pages = await get_homeworks(
                self.bot.http_client,
                self.api_url,
                classroom_secret,
                api_operations.listHomeworksCriteria(
                    count=15,
                    assigned_before_date=today_date,
                    assigned_after_date=today_date,
                ),
            )

            if daily_homeworks is None:
                continue

            daily_embed = make_homework_embed(
                daily_homeworks,
                "Daily Homework",
                pages=pages,
                color=self.bot.main_color,
            )

            await send_notifications(self.bot, notifies_daily, daily_embed)

            for before_due, user_ids in notifies_due.items():
                due_date = (
                    datetime.datetime.utcnow()
                    + timezone_delta
                    + datetime.timedelta(days=int(before_due))
                ).strftime("%Y-%m-%d")

                tomorrow_date = (
                    datetime.datetime.utcnow()
                    + timezone_delta
                    + datetime.timedelta(days=1)
                ).strftime("%Y-%m-%d")

                due_homeworks, pages = await get_homeworks(
                    self.bot.http_client,
                    self.api_url,
                    classroom_secret,
                    api_operations.listHomeworksCriteria(
                        count=15,
                        due_before_date=due_date,
                        due_after_date=tomorrow_date,
                    ),
                )

                if due_homeworks is None:
                    continue

                due_embed = make_homework_embed(
                    due_homeworks,
                    f"{before_due} Days Until Due",
                    pages=pages,
                    color=self.bot.main_color,
                )

                await send_notifications(self.bot, user_ids, due_embed)

    @send_notify.before_loop
    async def before_send_notify(self):
        await self.bot.wait_until_ready()
