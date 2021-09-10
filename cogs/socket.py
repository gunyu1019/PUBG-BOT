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
along with PUBG BOT.  If not, see <https://www.gnu.org/licenses/>.
"""

import logging
import inspect
import discord
import importlib
import os

from discord.ext import commands
from discord.state import ConnectionState
from typing import Union, List, Dict

from config.config import parser
from module.interaction import SlashContext, ComponentsContext
from module.message import Message
from module.commands import Command
from process.discord_exception import inspection, canceled
from utils.directory import directory
from utils.prefix import get_prefix
from utils.perm import permission

logger = logging.getLogger(__name__)
DBS = None


class SocketReceive(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.func: List[Dict[str, Command]] = []
        cogs = ["commands." + file[:-3] for file in os.listdir(f"{directory}/commands") if file.endswith(".py")]
        for cog in cogs:
            module = importlib.import_module(cog)
            _class = getattr(module, "setup")(self.bot)
            for func, attr in inspect.getmembers(_class):
                if isinstance(attr, Command):
                    self.func.append({"class": _class, "func": attr})

    @staticmethod
    def check_interaction(ctx: Union[SlashContext, Message], func: Command):
        if isinstance(ctx, SlashContext):
            return func.interaction
        elif isinstance(ctx, Message):
            return func.message

    @commands.Cog.listener()
    async def on_interaction_command(self, ctx: Union[SlashContext, Message]):
        if isinstance(ctx, Message):
            prefixes = get_prefix(self.bot, ctx)
            name = ""
            for prefix in prefixes:
                prefix_length = len(prefix)
                cc = ctx.content[prefix_length:]
                prefix_cc = ctx.content[0:prefix_length]
                if prefix_cc == prefix:
                    name = cc.split()
                    break
            if len(name) >= 1:
                ctx.name = name[0]
            elif len(name) < 1:
                return

        name = ctx.name

        _state: ConnectionState = getattr(self.bot, "_connection")
        for func in self.func:
            _function = func.get("func")
            if (_function.name == name or name in _function.aliases) and self.check_interaction(ctx, _function):
                _state.dispatch("command", ctx)
                if permission(_function.permission)(ctx):
                    if parser.getboolean("Inspection", "inspection") and not permission(1)(ctx):
                        await inspection(ctx)
                        return
                    try:
                        await _function.callback(func.get("class"), ctx)
                    except Exception as error:
                        _state.dispatch("command_exception", ctx, error)
                    else:
                        _state.dispatch("command_complete", ctx)
                else:
                    _state.dispatch("command_permission_error", ctx)
                break
        return

    @commands.Cog.listener()
    async def on_interaction_components(self, components: ComponentsContext):
        listeners = getattr(self.bot, "_listeners", {}).get("components", [])
        find_interaction = None
        for index, (future, check) in enumerate(listeners):
            removed = []
            if future.cancelled():
                removed.append(index)
                continue

            try:
                result = check(components)
            except Exception as exc:
                future.set_exception(exc)
                removed.append(index)
            else:
                if result:
                    find_interaction = components
                    future.set_result(components)
                    removed.append(index)

                if len(removed) == len(listeners):
                    getattr(self.bot, "_listeners", {}).pop("components")
                else:
                    for idx in reversed(removed):
                        del listeners[idx]

        for event in self.bot.extra_events.get("on_components", []):
            getattr(self.bot, "_schedule_event")(event, "on_components", components)

        if find_interaction is None:
            await canceled(components)
        return

    @commands.Cog.listener()
    async def on_socket_raw_receive(self, msg):
        if type(msg) is bytes:
            self.bot._buffer.extend(msg)

            if len(msg) < 4 or msg[-4:] != b'\x00\x00\xff\xff':
                return
            msg = getattr(self.bot, "_zlib").decompress(self.bot._buffer)
            msg = msg.decode('utf-8')
            self.bot._buffer = bytearray()
        payload = getattr(discord.utils, "_from_json")(msg)

        data = payload.get("d", {})
        t = payload.get("t", "")
        op = payload.get("op", "")

        if t == "PRESENCE_UPDATE" or op != 0:
            return

        logger.debug(payload)

        state: ConnectionState = getattr(self.bot, "_connection")
        if t == "INTERACTION_CREATE":
            if data.get("type") == 2:
                result = SlashContext(data, self.bot)
                state.dispatch('interaction_command', result)
            elif data.get("type") == 3:
                result = ComponentsContext(data, self.bot)
                state.dispatch('interaction_components', result)
            return
        elif t == "MESSAGE_CREATE":
            channel, _ = getattr(state, "_get_guild_channel")(data)
            message = Message(state=state, data=data, channel=channel)
            state.dispatch('interaction_command', message)
            return
        return


def setup(client):
    client.add_cog(SocketReceive(client))
