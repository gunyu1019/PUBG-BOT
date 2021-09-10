"""MIT License

Copyright (c) 2021 gunyu1019

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import discord

from discord.state import ConnectionState
from typing import List, Union

from module.components import ActionRow, Button, Selection, from_payload
from module.errors import InvalidArgument
from module.http import HttpClient
from utils.prefix import get_prefix


def _files_to_form(files: list, payload: dict):
    form = [{'name': 'payload_json', 'value': getattr(discord.utils, "_to_json")(payload)}]
    if len(files) == 1:
        file = files[0]
        form.append(
            {
                'name': 'file',
                'value': file.fp,
                'filename': file.filename,
                'content_type': 'application/octet-stream',
            }
        )
    else:
        for index, file in enumerate(files):
            form.append(
                {
                    'name': f'file{index}',
                    'value': file.fp,
                    'filename': file.filename,
                    'content_type': 'application/octet-stream',
                }
            )
    return form


def _allowed_mentions(state, allowed_mentions):
    if allowed_mentions is not None:
        if state.allowed_mentions is not None:
            allowed_mentions = state.allowed_mentions.merge(allowed_mentions).to_dict()
        else:
            allowed_mentions = allowed_mentions.to_dict()
    else:
        allowed_mentions = state.allowed_mentions and state.allowed_mentions.to_dict()
    return allowed_mentions


def _get_payload(
        content=None,
        embed=None,
        tts: bool = False,
        allowed_mentions=None,
        components=None
) -> dict:
    payload = {'tts': tts}
    if content:
        payload['content'] = content
    if embed:
        payload['embeds'] = embed
    if allowed_mentions:
        payload['allowed_mentions'] = allowed_mentions
    if components:
        payload['components'] = components
    return payload


class Message(discord.Message):
    def __init__(
            self,
            *,
            state: ConnectionState,
            channel: Union[discord.TextChannel, discord.DMChannel, discord.GroupChannel],
            data: dict
    ):
        if "message_reference" in data and "channel_id" not in data.get("message_reference", {}):
            data["message_reference"]["channel_id"] = channel.id
        super().__init__(state=state, channel=channel, data=data)
        self.components = from_payload(data.get("components", []))
        self.http = HttpClient(http=self._state.http)

    @property
    def prefix(self):
        return get_prefix(None, self)[0]

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
            components: List[Union[ActionRow, Button, Selection]] = None
    ):
        channel = MessageSendable(state=self._state, channel=self.channel)
        return await channel.send(
            content=content,
            tts=tts,
            embed=embed,
            embeds=embeds,
            file=file,
            files=files,
            allowed_mentions=allowed_mentions,
            components=components
        )

    async def edit(
            self,
            content=None,
            *,
            embed: discord.Embed = None,
            embeds: List[discord.Embed] = None,
            file: discord.File = None,
            files: List[discord.File] = None,
            allowed_mentions: discord.AllowedMentions = None,
            components: List[Union[ActionRow, Button, Selection]] = None
    ):
        if file is not None and files is not None:
            raise InvalidArgument()
        if embed is not None and embeds is not None:
            raise InvalidArgument()

        content = str(content) if content is not None else None
        if embed is not None:
            embeds = [embed]
        if embeds is not None:
            embeds = [embed.to_dict() for embed in embeds]
        if file:
            files = [file]
        if components is not None:
            components = [i.to_all_dict() if isinstance(i, ActionRow) else i.to_dict() for i in components]

        allowed_mentions = _allowed_mentions(self._state, allowed_mentions)

        payload = _get_payload(
            content=content,
            embed=embeds,
            allowed_mentions=allowed_mentions,
            components=components,
        )

        if files:
            payload["attachments"] = []
            form = _files_to_form(files=files, payload=payload)
        else:
            form = None

        await self.http.edit_message(
            channel_id=self.channel.id, message_id=self.id,
            payload=payload, form=form, files=files
        )

        if files:
            for file in files:
                file.close()
        return


class MessageCommand(Message):
    def __init__(
            self,
            *,
            state: ConnectionState,
            channel: Union[discord.TextChannel, discord.DMChannel, discord.GroupChannel],
            data: dict
    ):
        super().__init__(state=state, channel=channel, data=data)

        options = self.content.split()

        if len(options) >= 1:
            self.name = options[0]
        else:
            self.name = None

        if len(options) >= 2:
            self.options = self.content.split()[1:]
        else:
            self.options = []


class MessageSendable:
    def __init__(self, state: ConnectionState, channel):
        self._state = state
        self.http = HttpClient(http=self._state.http)
        self.channel = channel

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
            components: List[Union[ActionRow, Button, Selection]] = None
    ):
        if file is not None and files is not None:
            raise InvalidArgument()
        if embed is not None and embeds is not None:
            raise InvalidArgument()

        content = str(content) if content is not None else None
        if embed is not None:
            embeds = [embed]
        if embeds is not None:
            embeds = [embed.to_dict() for embed in embeds]
        if file:
            files = [file]
        if components is not None:
            components = [i.to_all_dict() if isinstance(i, ActionRow) else i.to_dict() for i in components]
        allowed_mentions = _allowed_mentions(self._state, allowed_mentions)

        payload = _get_payload(
            content=content,
            tts=tts,
            embed=embeds,
            allowed_mentions=allowed_mentions,
            components=components,
        )

        if files:
            form = _files_to_form(files=files, payload=payload)
            resp = await self.http.create_message(form=form, files=files, channel_id=self.channel.id)
        else:
            resp = await self.http.create_message(payload=payload, channel_id=self.channel.id)
        ret = Message(state=self._state, channel=self.channel, data=resp)

        if files:
            for i in files:
                i.close()
        return ret
