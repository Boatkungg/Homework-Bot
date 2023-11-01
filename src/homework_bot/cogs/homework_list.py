from typing import Optional
from dataclasses import dataclass

import discord
from discord import ApplicationContext, Embed, Interaction, ui
from discord.ext import commands


@dataclass
class HWListCriteria:
    assigned_before: Optional[str] = None
    assigned_after: Optional[str] = None
    due_before: Optional[str] = None
    due_after: Optional[str] = None


class HWListUI(ui.View):
    def __init__(
        self,
        bot,
        api_url,
        filter_criteria: HWListCriteria,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.bot = bot
        self.api_url = api_url
        self.filter_criteria = filter_criteria

        self.page = 1
        self.max_page = None

    async def get_homeworks(self, guild_id: int, page: int):
        db_query = await self.bot.db.fetch(
            """
            SELECT * FROM servers
            WHERE ServerID = :server_id
            """,
            {"server_id": guild_id},
        )

        if db_query is None:
            return None

        classroom_secret = db_query["ClassroomSecret"]

        query_params = {
            "secret": classroom_secret,
            "count": 10,
            "page": page,
        }

        for key, value in self.filter_criteria.__dict__.items():
            if value is not None:
                query_params[key] = value

        api_response = await self.bot.http_client.get(
            self.api_url + "/api/get_homeworks",
            json=query_params,
        )

        json_response = api_response.json()

        if json_response["response"]["error"] is not None:
            return None

        return json_response["response"]["context"]["homeworks"]

    async def get_max_page(self, guild_id: int):
        db_query = await self.bot.db.fetch(
            """
            SELECT * FROM servers
            WHERE ServerID = :server_id
            """,
            {"server_id": guild_id},
        )

        if db_query is None:
            return None

        classroom_secret = db_query["ClassroomSecret"]

        query_params = {
            "secret": classroom_secret,
            "count": 10,
        }

        for key, value in self.filter_criteria.__dict__.items():
            if value is not None:
                query_params[key] = value

        api_response = await self.bot.http_client.get(
            self.api_url + "/api/get_page_count",
            json=query_params,
        )

        json_response = api_response.json()

        if json_response["response"]["error"] is not None:
            return None

        return json_response["response"]["context"]["pages"]

    async def create_embed(self, page: int):
        if self.max_page is None:  # TODO: might be a problem
            self.max_page = await self.get_max_page()

        homeworks = await self.get_homeworks(page)

        if homeworks is None:
            return None

        embed = Embed("Homework List")  # pylint: disable=too-many-function-args
        embed.set_footer(text=f"Page {page}/{self.max_page}")

        for homework in homeworks:
            embed.add_field(
                name=f"{homework['subject']} - {homework['title']} ID: {homework['homework_id']}",
                value=f"Assigned at: {homework['assigned_at']}\nDue at: {homework['due_at']}",
                inline=False,
            )

        return embed
    
    async def send(self, ctx: ApplicationContext):
        self.message = await ctx.send(view=self)

    def update_embed(self):
        await self.message.edit(embed=)

    # TODO: change the respond in future
    @ui.button(label="Previous", style=discord.ButtonStyle.primary, emoji="⬅️")
    async def previous(self, interaction: Interaction, button: ui.Button):
        pass

    # TODO: change the respond in future
    @ui.button(label="Next", style=discord.ButtonStyle.primary, emoji="➡️")
    async def next(self, interaction: Interaction, button: ui.Button):
        pass


class HWList(commands.Cog):
    def __init__(self, bot, api_url):
        self.bot = bot
        self.api_url = api_url

    @commands.guild_only()
    @commands.slash_command()
    async def list(
        self,
        ctx: ApplicationContext,
        assigned_at: Optional[str],
        due_at: Optional[str],
        assigned_before: Optional[str],
        assigned_after: Optional[str],
        due_before: Optional[str],
        due_after: Optional[str],
    ):
        pass
