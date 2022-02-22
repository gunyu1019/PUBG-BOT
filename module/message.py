import asyncio
import datetime
from typing import Union, Optional, List

import discord
from discord.ext import interaction


class MessageCommand:
    def __init__(
            self,
            message: interaction.Message,
            client: interaction.Client
    ):
        self.client = client
        self._state = getattr(client, "_connection")
        self.message = message

        self.content = message.content
        options = self.content.split()
        self.name = None
        if len(options) >= 1:
            self.name = options[0]

        self.options = []
        if len(options) >= 2:
            self.options = self.content.split()[1:]

        self.prefix = None

        self.deferred = False
        self.responded = False
        self.deferred_task: Optional[asyncio.Task] = None

    @property
    def id(self) -> int:
        return self.message.id

    @property
    def channel(self) -> discord.abc.Messageable:
        return self.message.channel

    @property
    def guild(self) -> Optional[discord.Guild]:
        return self.message.guild

    @property
    def author(self) -> Optional[discord.abc.User]:
        return self.message.author

    @property
    def created_at(self) -> Optional[datetime.datetime]:
        return self.message.created_at

    @property
    def embeds(self) -> List[discord.Embed]:
        return self.message.embeds

    @property
    def components(self) -> List[interaction.Components]:
        return self.message.components

    @property
    def voice_client(self) -> Optional[discord.VoiceClient]:
        if self.guild is None:
            return None
        return self.guild.voice_client

    @staticmethod
    def _typing_done_callback(fut: asyncio.Future) -> None:
        # just retrieve any exception and call it a day
        try:
            fut.exception()
        except (asyncio.CancelledError, Exception):
            pass

    async def _do_deferred(self) -> None:
        for count in range(0, 300, 5):
            await self.channel.trigger_typing()
            if not self.deferred:
                break
            await asyncio.sleep(5)

    async def defer(
            self,
            _: bool = None
    ) -> None:
        if self.deferred:
            raise interaction.AlreadyDeferred()
        self.deferred = True
        self.responded = True
        self.deferred_task = self._state.loop.create_task(self._do_deferred())
        self.deferred_task.add_done_callback(self._typing_done_callback)
        return

    async def send(
            self,
            content=None,
            *,
            tts: bool = False,
            embed: discord.Embed = None,
            embeds: List[discord.Embed] = None,
            file: discord.File = None,
            files: List[discord.File] = None,
            allowed_mentions: discord.AllowedMentions = None,
            components: List[Union[interaction.ActionRow, interaction.Button, interaction.Selection]] = None
    ) -> Optional[interaction.Message]:
        self.deferred = False
        if self.deferred_task is not None:
            if not self.deferred_task.cancelled():
                self.deferred_task.cancel()
        self.responded = True
        channel = interaction.MessageSendable(state=self._state, channel=self.channel)
        return await channel.send(
            content=content,
            tts=tts,
            embed=embed,
            embeds=embeds,
            file=file,
            files=files,
            allowed_mentions=allowed_mentions,
            reference=self.message,
            mention_author=False,
            components=components
        )
