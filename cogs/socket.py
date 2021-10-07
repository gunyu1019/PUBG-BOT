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
import importlib.util
import os

from discord.ext import commands
from discord.state import ConnectionState
from typing import Union, List, Dict

from config.config import parser
from module.interaction import ApplicationContext, ComponentsContext
from module.message import MessageCommand, Message
from module.commands import Command
from process.discord_exception import inspection, canceled
from utils.directory import directory
from utils.perm import permission

logger = logging.getLogger(__name__)
DBS = None


class SocketReceive(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.commands: Dict[str, Command] = {}
        cogs = ["commands." + file[:-3] for file in os.listdir(f"{directory}/commands") if file.endswith(".py")]

        for cog in cogs:
            spec = importlib.util.find_spec(cog)
            if spec is None:
                raise discord.ext.commands.errors.ExtensionNotFound(cog)

            lib = importlib.util.module_from_spec(spec)
            try:
                spec.loader.exec_module(lib)  # type: ignore
            except Exception as e:
                raise discord.ext.commands.errors.ExtensionFailed(cog, e) from e

            try:
                _setup = getattr(lib, 'setup')
            except AttributeError:
                raise discord.ext.commands.errors.NoEntryPointError(cog)

            try:
                _cog = _setup(self.bot)
            except Exception as e:
                raise discord.ext.commands.errors.ExtensionFailed(cog, e) from e

            for func, attr in inspect.getmembers(_cog):
                if isinstance(attr, Command):
                    attr.parents = _cog
                    self.commands[attr.name] = attr
                    if len(attr.aliases) != 0:
                        for alias in attr.aliases:
                            self.commands[alias] = attr

    @staticmethod
    def check_interaction(ctx: Union[ApplicationContext, MessageCommand], func: Command):
        if isinstance(ctx, ApplicationContext):
            return func.interaction
        elif isinstance(ctx, MessageCommand):
            return func.message

    async def get_prefix(self, ctx) -> List[str]:
        prefix = ret = self.bot.command_prefix
        if callable(prefix):
            ret = await discord.utils.maybe_coroutine(prefix, self, ctx)

        if not isinstance(ret, str):
            try:
                ret = list(ret)
            except TypeError:
                raise TypeError("command_prefix must be plain string, iterable of strings, or callable "
                                f"returning either of these, not {ret.__class__.__name__}")

            if not ret:
                raise ValueError("Iterable command_prefix must contain at least one prefix")

        return ret

    @commands.Cog.listener()
    async def on_interaction_command(self, ctx: Union[ApplicationContext, MessageCommand]):
        prefixes = await self.get_prefix(ctx)
        ctx.prefix = prefixes
        if isinstance(ctx, MessageCommand):
            if isinstance(prefixes, list):
                if not ctx.content.startswith(tuple(prefixes)):
                    return

                find_prefix = None
                for prefix in prefixes:
                    prefix_len = len(prefix)
                    if ctx.content[0:prefix_len] == prefix:
                        find_prefix = prefix
                        break
                if find_prefix is None:
                    raise

                ctx.command_prefix = find_prefix
                ctx.name = ctx.name[len(find_prefix):]
            elif isinstance(prefixes, str):
                if not ctx.content.startswith(prefixes):
                    return
                prefix_len = len(prefixes)
                ctx.command_prefix = ctx.content[0:prefix_len]
                ctx.name = ctx.name[prefix_len:]

        _state: ConnectionState = getattr(self.bot, "_connection")
        command = self.commands.get(ctx.name)
        if command is None:
            return

        _function = command
        # if (_function.name == ctx.name or ctx.name in _function.aliases) and self.check_interaction(ctx, _function):
        if not self.check_interaction(ctx, _function):
            return
        _state.dispatch("command", ctx)
        if permission(_function.permission)(ctx):
            if parser.getboolean("Inspection", "inspection") and not permission(1)(ctx):
                await inspection(ctx)
                return

            try:
                await _function.callback(_function.parents, ctx)
            except Exception as error:
                _state.dispatch("command_exception", ctx, error)
            else:
                _state.dispatch("command_complete", ctx)
        else:
            _state.dispatch("command_permission_error", ctx)
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
                result = ApplicationContext(data, self.bot)
                state.dispatch('interaction_command', result)
            elif data.get("type") == 3:
                result = ComponentsContext(data, self.bot)
                state.dispatch('interaction_components', result)
            return
        elif t == "MESSAGE_CREATE":
            channel, _ = getattr(state, "_get_guild_channel")(data)
            message = Message(state=state, data=data, channel=channel)
            command = MessageCommand(state=state, data=data, channel=channel)
            state.dispatch('interaction_message', message)
            state.dispatch('interaction_command', command)
            return
        return


def setup(client):
    client.add_cog(SocketReceive(client))
