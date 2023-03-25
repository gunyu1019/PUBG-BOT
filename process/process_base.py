from abc import ABCMeta

import discord
from discord.ext import interaction
from sqlalchemy.orm import sessionmaker

from module import pubgpy
from process.favorite import FavoriteBasic
from process.response_base import ResponseBase


class ProcessBase(FavoriteBasic, ResponseBase, metaclass=ABCMeta):
    def __init__(
        self,
        ctx: interaction.ApplicationContext,
        client: interaction.Client,
        factory: sessionmaker,
        player: pubgpy.Player,
    ):
        super(ProcessBase, self).__init__(
            ctx=ctx, client=client, factory=factory, player=player
        )
        self.normal_stats_button: interaction.Button | None = None
        self.ranked_stats_button: interaction.Button | None = None
        self.matches_stats_button: interaction.Button | None = None
        self.favorite_stats_button: interaction.Button | None = None
        self.update_stats_button: interaction.Button | None = None
        self.init_button()

    def init_button(self):
        self.normal_stats_button = interaction.Button(
            custom_id="normal_stats_button",
            emoji=discord.PartialEmoji(name="\U00000031\U0000FE0F\U000020E3"),
            style=1,
        )
        self.ranked_stats_button = interaction.Button(
            custom_id="ranked_stats_button",
            emoji=discord.PartialEmoji(name="\U00000032\U0000FE0F\U000020E3"),
            style=1,
        )
        self.matches_stats_button = interaction.Button(
            custom_id="matches_stats_button",
            emoji=discord.PartialEmoji(name="\U00000033\U0000FE0F\U000020E3"),
            style=1,
        )
        favorite = self.is_favorite
        if favorite is None:
            favorite = FavoriteBasic
        self.favorite_stats_button = interaction.Button(
            custom_id="favorite_stats_button",
            emoji=discord.PartialEmoji(
                name="\U00002B50" if not favorite else "\U0001F31F"
            ),
            style=1,
        )
        self.update_stats_button = interaction.Button(
            custom_id="update_stats_button",
            emoji=discord.PartialEmoji(id=868344053262061578, name="update"),
            style=1,
        )

    @property
    def buttons(self) -> interaction.ActionRow:
        return interaction.ActionRow(
            components=[
                self.normal_stats_button,
                self.ranked_stats_button,
                self.matches_stats_button,
                self.favorite_stats_button,
                self.update_stats_button,
            ]
        )
