import calendar
import datetime
import io
from typing import Optional

import discord
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from cacheout import Cache
from discord import (   # pylint: disable=no-name-in-module
    ApplicationContext,
    Colour,
    Option,
)
from discord.ext import commands
from pycord.multicog import add_to_group

from homework_bot import api_operations, db_operations, responses, utils

offset = datetime.timedelta(days=1)

sns.set_theme(style="darkgrid")


@Cache(maxsize=50, ttl=300).memoize()
def plot_statistic_calendar(stats: dict, title: str, date: datetime.date = None):
    date = datetime.date.today() if date is None else date

    first_day = date.replace(day=1)
    calendar_labels = utils.calendar_label(first_day.year, first_day.month)

    calendar_offset = (first_day + offset).isocalendar()[1]

    array = np.zeros((len(calendar_labels), 7))

    for key, value in stats.items():
        date = datetime.datetime.strptime(key, "%Y-%m-%d").isocalendar()
        if date[2] == 7:
            day = 0
            array[date[1] - calendar_offset + 1][day] = value
        else:
            day = date[2]
            array[date[1] - calendar_offset][day] = value

    fig, ax = plt.subplots(figsize=(7, 5))

    cmap = sns.color_palette("light:#ff7878", as_cmap=True)
    sns.heatmap(
        array,
        annot=calendar_labels,
        fmt="s",
        cmap=cmap,
        cbar=True,
        ax=ax,
        xticklabels=["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
        yticklabels=False,
    )

    ax.set_title(title)
    ax.set(xlabel="", ylabel="")
    ax.xaxis.tick_top()

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    file = discord.File(buf, filename="statistic.png")

    return file


@Cache(maxsize=50, ttl=300).memoize()
def plot_statistic_graph(stats: dict, title: str, date: datetime.date = None):
    date = datetime.date.today() if date is None else date

    first_day = date.replace(day=1)
    last_day = date.replace(day=calendar.monthrange(first_day.year, first_day.month)[1])

    days = np.arange(first_day.day, last_day.day + 1)
    values = np.zeros(len(days))

    for key, value in stats.items():
        date = datetime.datetime.strptime(key, "%Y-%m-%d")
        values[date.day - 1] = value

    fig, ax = plt.subplots(figsize=(7, 5))

    sns.lineplot(x=days, y=values, color="#ff7878", ax=ax)
    ax.set_title(title)
    ax.set(xlabel="Day", ylabel="Homeworks")

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    file = discord.File(buf, filename="statistic.png")

    return file


class HWStatistic(commands.Cog):
    def __init__(self, bot, api_url):
        self.bot = bot
        self.api_url = api_url

    @add_to_group("homework")
    @commands.slash_command(description="Get homework statistic")
    async def statistic(
        self,
        ctx: ApplicationContext,
        style: Option(str, choices=["graph", "calendar"], default="calendar"),
        month: Option(
            int,
            description="Month of the statistic",
            choices=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
            default=datetime.date.today().month,
        ),
        year: Optional[int] = datetime.date.today().year,
        subject: Optional[str] = None,
    ):
        await ctx.defer()
        db_query = await db_operations.get_guild(self.bot.db, ctx.guild.id)

        if db_query is None:
            await responses.normal_response(
                ctx, "**Classroom not set**", color=self.bot.main_color
            )
            return

        stat_month = datetime.date.today().replace(day=1, month=month, year=year)

        first_day = stat_month
        last_day = stat_month.replace(
            day=calendar.monthrange(first_day.year, first_day.month)[1]
        )

        json_response, error = await api_operations.get_statistics(
            self.bot.http_client,
            self.api_url,
            db_query["ClassroomSecret"],
            api_operations.getStatisticsCriteria(
                subject, last_day.strftime("%Y-%m-%d"), first_day.strftime("%Y-%m-%d")
            ),
        )

        if error is not None:
            await responses.normal_response(
                ctx, f"**Something went wrong**\nError: `{error}`", color=Colour.red()
            )
            return

        stats = json_response["response"]["context"]

        if len(stats) == 0:
            await responses.normal_response(
                ctx,
                f"**No statistic for this month** `{first_day.strftime('%B %Y')}`",
                color=Colour.red(),
            )
            return

        title = (
            f"Statistic for {subject} in {first_day.strftime('%B %Y')}"
            if subject is not None
            else f"Statistic in {first_day.strftime('%B %Y')}"
        )

        if style == "graph":
            file = plot_statistic_graph(stats, title, stat_month)
        else:
            file = plot_statistic_calendar(stats, title, stat_month)

        await ctx.respond(file=file)
