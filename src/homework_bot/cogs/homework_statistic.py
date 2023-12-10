import calendar
import datetime
import io

import discord
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from discord import ApplicationContext, Colour
from discord.ext import commands
from pycord.multicog import add_to_group

from homework_bot import api_operations, db_operations, responses, utils

offset = datetime.timedelta(days=1)


class HWStatistic(commands.Cog):
    def __init__(self, bot, api_url):
        self.bot = bot
        self.api_url = api_url

    @add_to_group("homework")
    @commands.slash_command()
    async def statistic(self, ctx: ApplicationContext, subject: str):
        await ctx.defer()
        db_query = await db_operations.get_guild(self.bot.db, ctx.guild.id)

        if db_query is None:
            await responses.normal_response(
                ctx, "**Classroom not set**", color=self.bot.main_color
            )
            return

        first_day = datetime.date.today().replace(day=1)
        last_day = datetime.date.today().replace(
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

        stats: dict = json_response["response"]["context"]

        if len(stats) == 0:
            await responses.normal_response(
                ctx, f"**No statistic for this subject** `{subject}`", color=Colour.red()
            )
            return

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

        ax.set_title(f"Statistic for {subject} in {first_day.strftime('%B %Y')}")
        ax.set(xlabel="", ylabel="")
        ax.xaxis.tick_top()

        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        file = discord.File(buf, filename="statistic.png")

        await ctx.respond(file=file)
