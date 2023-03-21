import asyncio
import copy
import discord
from discord.ext import interaction
from sqlalchemy.orm import sessionmaker

from module import pubgpy
from process.favorite import FavoriteBasic


class ProcessBase(FavoriteBasic):
    def __init__(
        self,
        ctx: interaction.ApplicationContext,
        factory: sessionmaker,
        player: pubgpy.Player,
    ):
        super(ProcessBase, self).__init__(ctx=ctx, factory=factory, player=player)
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

    async def response_component(
        self,
        component_context: interaction.ComponentsContext | None = None,
        content: str = discord.utils.MISSING,
        attachments: list[discord.File] = discord.utils.MISSING,
        **kwargs
    ) -> interaction.ComponentsContext | None:
        if component_context is None:
            message = await self.context.edit(
                content=content,
                embeds=[],
                attachments=attachments,
                components=[self.buttons],
            )
        else:
            message = await component_context.edit(
                content=content,
                embeds=[],
                attachments=attachments,
                components=[self.buttons],
            )

        try:
            context: interaction.ComponentsContext = (
                await self.client.wait_for_global_component(
                    check=(
                        lambda x: x.custom_id in [t.custom_id for t in self.buttons.components] and
                        x.message.id == message.id and x.channel.id == self.context.channel.id
                    ),
                    timeout=300,
                )
            )
        except asyncio.TimeoutError:
            await self.cancel_component(component_context, content, **kwargs)
            return

        await context.defer_update()
        return context

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

    async def cancel_component(
        self,
        component_context: interaction.ComponentsContext | None = None,
        content: str = None,
        **kwargs
    ):
        component = copy.copy(self.buttons)
        for index, _ in enumerate(self.buttons.components):
            component.components[index].disabled = True
            component.components[index].style = 2

        if component_context is not None:
            await component_context.edit(
                content=content, embeds=[], components=[component], **kwargs
            )
        else:
            await self.context.edit(
                content=content, embeds=[], components=[component], **kwargs
            )
        return
