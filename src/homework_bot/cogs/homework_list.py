from dataclasses import dataclass
from typing import Optional

import discord
from discord import ApplicationContext, Embed, Interaction, ui
from discord.ext import commands

from homework_bot import api_operations, db_operations


@dataclass
class HWListCriteria:
    assigned_before: Optional[str] = None
    assigned_after: Optional[str] = None
    due_before: Optional[str] = None
    due_after: Optional[str] = None


class HWListUI(ui.View):
    def __init__(self, bot, api_url, classroom_secret, criteria: HWListCriteria):
        super().__init__(timeout=60)
        self.page = 1
        self.max_page = 0

        self.bot = bot
        self.api_url = api_url

        self.classroom_secret = classroom_secret
        self.criteria = criteria

    async def on_timeout(self):
        self.disable_all_items()
        await self.message.edit_original_response(view=self)

    async def get_homeworks(self):
        criteria = api_operations.getHomeworksCriteria(
            count=6,
            page=self.page,
            assigned_before_date=self.criteria.assigned_before,
            assigned_after_date=self.criteria.assigned_after,
            due_before_date=self.criteria.due_before,
            due_after_date=self.criteria.due_after,
        )

        json_response, _ = await api_operations.get_homeworks(
            self.bot.http_client,
            self.api_url,
            self.classroom_secret,
            criteria,
        )

        json_response_formatted = [
            {
                "homework_id": homework["homework_id"],
                "subject": homework["subject"],
                "assigned_date": homework["assigned_date"],
                "due_date": homework["due_date"],
            }
            for homework in json_response["response"]["context"]["homeworks"]
        ]

        return json_response_formatted, json_response["response"]["context"]["max_page"]

    async def create_embed(self):
        homeworks, self.max_page = await self.get_homeworks()

        if self.max_page == 0:
            embed = Embed(title="Homework", timestamp=discord.utils.utcnow())
            embed.set_footer(text="Homework not found")
            return embed

        embed = Embed(title="Homework", timestamp=discord.utils.utcnow())
        embed.set_footer(text=f"Page {self.page}/{self.max_page}")

        # 1 • A31101
        # assigned 12/03/1212 • due 14/03/1212
        # ---
        # 2 • B31102
        # assigned 12/03/1212 • due 14/03/1212

        description = "```\n"
        for homework in homeworks:
            description += f"#{homework['homework_id']} • {homework['subject']}\n"
            description += (
                f"assigned {homework['assigned_date']} • due {homework['due_date']}\n"
            )
            description += "---\n"

        description += "```"

        embed.description = description

        return embed

    async def update_page(self):
        embed = await self.create_embed()
        self.update_button()

        await self.message.edit_original_response(embed=embed, view=self)

    def update_button(self):
        frst, prev, nxt, last = None, None, None, None
        for child in self.children:
            if isinstance(child, ui.Button) and child.label == "First":
                frst = child

            elif isinstance(child, ui.Button) and child.label == "Previous":
                prev = child

            elif isinstance(child, ui.Button) and child.label == "Next":
                nxt = child

            elif isinstance(child, ui.Button) and child.label == "Last":
                last = child

            if frst and prev and nxt and last:
                break

        if self.max_page == 0:
            self.disable_all_items()

        elif self.page <= 1:
            frst.disabled = True
            prev.disabled = True
            nxt.disabled = False
            last.disabled = False

        elif self.page >= self.max_page:
            frst.disabled = False
            prev.disabled = False
            nxt.disabled = True
            last.disabled = True

        else:
            frst.disabled = False
            prev.disabled = False
            nxt.disabled = False
            last.disabled = False

    async def send_initial_message(self, ctx: ApplicationContext):
        embed = await self.create_embed()
        self.update_button()

        self.message = await ctx.respond(embed=embed, view=self)

    @ui.button(label="First", style=discord.ButtonStyle.blurple, emoji="⏮️")
    async def first(
        self, button: ui.Button, interaction: Interaction
    ):  # pylint: disable=unused-argument
        await interaction.response.defer()
        self.page = 1

        await self.update_page()

    @ui.button(label="Previous", style=discord.ButtonStyle.blurple, emoji="⬅️")
    async def previous(
        self, button: ui.Button, interaction: Interaction
    ):  # pylint: disable=unused-argument
        await interaction.response.defer()
        self.page -= 1

        await self.update_page()

    @ui.button(label="Next", style=discord.ButtonStyle.blurple, emoji="➡️")
    async def next(
        self, button: ui.Button, interaction: Interaction
    ):  # pylint: disable=unused-argument
        await interaction.response.defer()
        self.page += 1

        await self.update_page()

    @ui.button(label="Last", style=discord.ButtonStyle.blurple, emoji="⏭️")
    async def last(
        self, button: ui.Button, interaction: Interaction
    ):  # pylint: disable=unused-argument
        await interaction.response.defer()
        self.page = self.max_page

        await self.update_page()


class HWList(commands.Cog):
    def __init__(self, bot, api_url):
        self.bot = bot
        self.api_url = api_url

    @commands.guild_only()
    @commands.slash_command()
    async def list(
        self,
        ctx: ApplicationContext,
        assigned_at: Optional[str] = None,
        due_at: Optional[str] = None,
        assigned_before: Optional[str] = None,
        assigned_after: Optional[str] = None,
        due_before: Optional[str] = None,
        due_after: Optional[str] = None,
    ):
        await ctx.defer()
        db_query = await db_operations.get_classroom_secret(self.bot.db, ctx.guild_id)

        # TODO: change this in future
        if db_query["ClassroomSecret"] is None:
            await ctx.respond("Classroom not set!")
            return

        criteria = HWListCriteria()
        if assigned_at is not None:
            criteria.assigned_before = assigned_at
            criteria.assigned_after = assigned_at

        elif due_at is not None:
            criteria.due_before = due_at
            criteria.due_after = due_at

        else:
            criteria.assigned_before = assigned_before
            criteria.assigned_after = assigned_after
            criteria.due_before = due_before
            criteria.due_after = due_after

        list_ui = HWListUI(
            self.bot, self.api_url, db_query["ClassroomSecret"], criteria
        )

        await list_ui.send_initial_message(ctx)
