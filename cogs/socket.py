import logging
import inspect
import importlib
import os

from discord.ext import commands
from discord.channel import TextChannel
from discord.state import ConnectionState
from typing import Union, List, Dict
from module.interaction import SlashContext, Message
from module.commands import Command
from utils.directory import directory
from utils.prefix import get_prefix
from utils.perm import permission

logger = logging.getLogger(__name__)
DBS = None


def log_system(msg):
    logger.info(msg)


class SocketReceive(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.func: List[Dict[str, Command]] = []
        cogs = ["commands." + file[:-3] for file in os.listdir(f"{directory}/commands") if file.endswith(".py")]
        for cog in cogs:
            module = importlib.import_module(cog)
            _class = module.setup(self.bot)
            for func, attr in inspect.getmembers(_class):
                if isinstance(attr, Command):
                    self.func.append({"class": _class, "func": attr})

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
                    name = cc
                    break
        else:
            name = ctx.name

        if name not in [i.get("func").name for i in self.func]:
            return
        logger.info("On command: {}".format(name))
        for func in self.func:
            _function = func.get("func")
            if _function.name == name:
                await _function.callback(func.get("class"), ctx)
                break
        return

    @commands.Cog.listener()
    async def on_socket_response(self, payload: dict):
        data = payload.get("d", {})
        t = payload.get("t", "")

        if t == "PRESENCE_UPDATE":
            return

        logger.debug(payload)

        state: ConnectionState = getattr(self.bot, "_connection")
        if t == "INTERACTION_CREATE":
            if data.get("type") == 2:
                slash = SlashContext(data, self.bot)
                state.dispatch('interaction_command', slash)
            return
        elif t == "MESSAGE_CREATE":
            channel, _ = getattr(state, "_get_guild_channel")(data)
            message = Message(state=state, data=data, channel=channel)
            state.dispatch('interaction_command', message)
            if getattr(state, "_messages") is not None:
                getattr(state, "_messages").append(message)
            if channel and channel.__class__ is TextChannel:
                channel.last_message_id = message.id
            return
        return


def setup(client):
    client.add_cog(SocketReceive(client))
