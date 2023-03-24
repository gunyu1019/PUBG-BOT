"""GNU GENERAL PUBLIC LICENSE
Version 3, 29 June 2007

Copyright (c) 2021 gunyu1019

PUBG BOT is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

PUBG BOT is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with PUBG BOT.  If not, see <http://www.gnu.org/licenses/>.
"""

import json

import discord
from discord.ext import interaction

from config.config import get_config
from process.response_base import ResponseBase
from utils.directory import directory

parser = get_config()
with open(f"{directory}/data/command.json", "r", encoding='utf-8') as f:
    commands = json.load(f)


class Help(ResponseBase):
    def __init__(self, ctx: interaction.ApplicationContext, client: interaction.Client):
        super().__init__(ctx, client)
        self.ctx = ctx
        self.client = client

        self.page = None
        self._commands = list(commands.keys())

        self.left_btn = None
        self.cancel_btn = None
        self.right_btn = None
        self.init_button()

        self.color = int(parser.get("Color", "default"), 16)
        self.error_color = int(parser.get("Color", "error"), 16)
        self.warning_color = int(parser.get("Color", "warning"), 16)

    def init_button(self):
        self.left_btn = interaction.Button(
            style=1,
            emoji=discord.PartialEmoji(name="\U00002B05"),
            custom_id="left_page"
        )
        self.cancel_btn = interaction.Button(
            style=1,
            emoji=discord.PartialEmoji(name="\U0000274C"),
            custom_id="cancel"
        )
        self.right_btn = interaction.Button(
            style=1,
            emoji=discord.PartialEmoji(name="\U000027A1"),
            custom_id="right_page"
        )

    @property
    def buttons(self):
        return [
            self.left_btn,
            self.cancel_btn,
            self.right_btn
        ]

    def current_button(self):
        self.init_button()
        if self.page <= 0:
            self.left_btn.disabled = True
        elif self.page >= len(self._commands):
            self.right_btn.disabled = True
        return

    async def response_component(
            self,
            component_context: interaction.ComponentsContext | None = None,
            content: str = discord.utils.MISSING,
            embeds: list[discord.Embed] = None,
            attachments: list[discord.File] = discord.utils.MISSING,
            **kwargs
    ) -> interaction.ComponentsContext | None:
        response = await super().response_component(component_context, content, embeds, attachments, **kwargs)
        if response.custom_id == "cancel":
            return
        now_page = self.page
        if response.custom_id == "left_page":
            now_page -= 1
        elif response.custom_id == "right_page":
            now_page += 1

        if now_page <= 0:
            await self.first_page(component_context=response)
        else:
            await self.main_page(page=now_page, component_context=response)
        return

    async def first_page(self, component_context: interaction.ComponentsContext | None = None):
        self.page = 0
        embed = discord.Embed(
            title="소개",
            description="PUBG BOT을 이용해주셔서 감사합니다. PUBG BOT은 {}서버와 함께 발전해나가며, "
                        "배틀그라운드 게임 정보를 제공하는 봇입니다.\n"
                        "PUBG BOT은 오픈 소스로 제작되었으며 [링크](https://github.com/gunyu1019/PUBG-BOT)를 클릭하여 "
                        "소스코드를 확인하실 수 있습니다.\n\n "
                        "아래의 버튼을 클릭하여 명령어를 알아보세요!".format(len(self.client.guilds)),
            color=self.color)
        embed.set_author(name="PUBG BOT 도우미", icon_url=self.client.user.avatar.url)
        embed.set_footer(text="{}/{} 페이지".format(1, len(self._commands) + 1))
        self.current_button()

        await self.response_component(component_context=component_context, embeds=[embed])
        return

    async def main_page(self, page: int = 1, component_context: interaction.ComponentsContext | None = None):
        self.page = page
        embed = discord.Embed(color=self.color)
        embed.set_author(name="PUBG BOT 도우미", icon_url=self.client.user.avatar.url)
        embed.set_footer(text="{}/{} 페이지".format(page + 1, len(self._commands) + 1))

        command_key = self._commands[page - 1]
        command = commands.get(command_key, {})
        embed.title = command_key
        for _command in command:
            name = _command.get("name")
            description = _command.get("description")
            options = _command.get("options", [])
            inline = _command.get("inline", False)
            if options != [] and options is not None:
                options_comment = []
                for option in options:
                    option_name = option.get("name")
                    choices = option.get("choices")
                    if choices is not None:
                        option_comment = "|".join(choices)
                    else:
                        option_comment = option_name

                    if not option.get("required", False):
                        option_comment += "(선택)"
                    options_comment.append(option_comment)
                embed.add_field(name="/{} <{}>".format(
                    name, "> <".join(options_comment)
                ), value="{}{}\n".format(
                    description,
                ), inline=inline)
            else:
                embed.add_field(name="/{}".format(name), value="{}{}\n".format(
                    description,
                ), inline=inline)
        self.current_button()

        await self.response_component(component_context=component_context, embeds=[embed])
        return
