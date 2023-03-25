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
import copy
import json

import discord
from discord.ext import interaction

from config.config import get_config
from process.response_base import ResponseBase
from utils.location import comment

parser = get_config()
help_parser = get_config("help_config")


class Help(ResponseBase):
    def __init__(self, ctx: interaction.ApplicationContext, client: interaction.Client):
        super().__init__(ctx, client)
        self.ctx = ctx
        self.client = client

        self.page = None
        self._commands = [x for x in help_parser.sections() if x.endswith("Command")]

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
            custom_id="left_page",
        )
        self.cancel_btn = interaction.Button(
            style=1, emoji=discord.PartialEmoji(name="\U0000274C"), custom_id="cancel"
        )
        self.right_btn = interaction.Button(
            style=1,
            emoji=discord.PartialEmoji(name="\U000027A1"),
            custom_id="right_page",
        )

    @property
    def buttons(self):
        return interaction.ActionRow(
            components=[self.left_btn, self.cancel_btn, self.right_btn]
        )

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
        response = await super().response_component(
            component_context, content, embeds, attachments, **kwargs
        )
        if response.custom_id == "cancel":
            await self.cancel_component(
                component_context, content, embeds, attachments, **kwargs
            )
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

    async def first_page(
        self, component_context: interaction.ComponentsContext | None = None
    ):
        self.page = 0
        embed = discord.Embed(
            title=comment("help_process", "main_title", self.ctx.locale),
            description=comment(
                "help_process", "main_description", self.ctx.locale
            ).format(guild_count=len(self.client.guilds)),
            color=self.color,
        )
        embed.set_author(
            name=comment("help_process", "title", self.ctx.locale),
            icon_url=self.client.user.avatar.url,
        )
        embed.set_footer(
            text=comment("help_process", "footer", self.ctx.locale).format(
                current_page=1, max_page=len(self._commands) + 1
            )
        )
        self.current_button()

        await self.response_component(
            component_context=component_context, embeds=[embed]
        )
        return

    async def main_page(
        self,
        page: int = 1,
        component_context: interaction.ComponentsContext | None = None,
    ):
        self.page = page
        embed = discord.Embed(color=self.color)
        embed.set_author(
            name=comment("help_process", "title", self.ctx.locale),
            icon_url=self.client.user.avatar.url,
        )
        embed.set_footer(
            text=comment("help_process", "footer", self.ctx.locale).format(
                current_page=page + 1, max_page=len(self._commands) + 1
            )
        )

        command_section = self._commands[page - 1]
        embed.title = comment(
            "help_process",
            help_parser.get(command_section, "title", fallback="도움말"),
            self.ctx.locale,
        )

        commands = json.loads(
            help_parser.get(command_section, "commands", fallback="[]")
        )
        application_commands_info: dict[
            str, interaction.Command | interaction.SubCommand
        ] = {}
        for command in self.client.get_interaction():
            if (
                command.func.__name__ not in commands
                or command.type != interaction.ApplicationCommandType.CHAT_INPUT
            ):
                continue
            command: interaction.Command  # Type hint
            if command.is_subcommand:
                for option in command.options:
                    if isinstance(option, interaction.SubCommandGroup):
                        for _option in option.options:
                            application_commands_info[
                                "{m_command} {g_command} {sub_command}".format(
                                    m_command=command.name,
                                    g_command=option.name,
                                    sub_command=_option.name,
                                )
                            ] = _option
                        continue
                    application_commands_info[
                        "{m_command} {sub_command}".format(
                            m_command=command.name, sub_command=option.name
                        )
                    ] = option
            else:
                application_commands_info[command.name] = command

        for command_name, application_command in application_commands_info.items():
            opt: interaction.CommandOption
            options = [
                "[{name}{optional}]".format(
                    name=opt.name, optional=" (선택)" if not opt.required else ""
                )
                for opt in application_command.options
            ]
            embed.add_field(
                name="/{command_name} {options}".format(
                    command_name=command_name, options=" ".join(options)
                ),
                value=application_command.description,
                inline=False,
            )
        self.current_button()

        await self.response_component(
            component_context=component_context, embeds=[embed]
        )
        return
