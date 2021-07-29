import discord

from typing import Union
from module import pubgpy
from module.components import ActionRow, Button
from module.interaction import SlashContext, Message, ComponentsContext
from utils.cache import CacheData


class Match:
    def __init__(
            self,
            ctx: Union[SlashContext, Message],
            client: discord.Client,
            pubg: pubgpy.Client,
            player: str,
            player_id: str,
    ):
        self.ctx = ctx
        self.client = client
        self.pubg = pubg
        self.database = CacheData(self.pubg)
        self.player_nickname = player
        self.player_id = player_id
        self.player = self.pubg.player_id(self.player_id)

    async def choice_match(self):
        player_data = self.pubg.players(ids=[self.player_id])
        return
