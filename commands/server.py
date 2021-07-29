import discord
import json

from typing import Union

import pymysql.cursors

from module import commands
from module.interaction import SlashContext, Message
from utils.database import getDatabase


class Command:
    def __init__(self, bot):
        self.client = bot
        self.color = 0xffd619

    @commands.command(name="상태", permission=4)
    async def status(self, ctx: Union[SlashContext, Message]):
        return


def setup(client):
    return Command(client)
