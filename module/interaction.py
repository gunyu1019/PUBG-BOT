import discord
import logging

from discord.state import ConnectionState
from typing import Optional, List, Union

from module.components import ActionRow, Button, Selection, from_payload
from module.http import HttpClient, InteractionData

log = logging.getLogger()


def _files_to_form(files: list, payload: dict):
    form = [{'name': 'payload_json', 'value': discord.utils.to_json(payload)}]
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


class SlashContext:
    def __init__(self, payload: dict, client: discord.Client):
        self.client = client
        self.id = payload.get("id")
        self.version = payload.get("version")
        self.type = payload.get("type", 2)
        self.token = payload.get("token")
        self.application = payload.get("application_id")

        self._state: ConnectionState = getattr(client, "_connection")
        data = payload.get("data", {})
        guild_id = payload.get("guild_id")
        channel_id = payload.get("channel_id")
        self.guild: Optional[discord.Guild] = client.get_guild(int(guild_id))
        self.channel = self._state.get_channel(int(channel_id))

        if self.guild is not None:
            member = payload.get("member")
            self.author = discord.Member(data=member, state=self._state, guild=self.guild)
        else:
            user = payload.get("user")
            self.author = discord.User(data=user, state=self._state)

        self.name = data.get("name")
        self.options = {}

        self.deferred = False
        self.responded = False

        self.created_at = discord.utils.snowflake_time(int(self.id))

        for option in data.get("options", []):
            key = option.get("name")
            value = option.get("value")
            option_type = option.get("type")
            if option_type == 3:
                self.options[key]: str = value
            elif option_type == 4:
                self.options[key]: int = value
            elif option_type == 5:
                self.options[key] = bool(value)
            elif option_type == 6:
                if self.guild is not None:
                    self.member = self.guild.get_member(value)
                else:
                    self.member = client.get_user(value)
            elif option_type == 7 and self.guild is not None:
                self.options[key] = self.guild.get_channel(value)
            elif option_type == 8:
                self.options[key]: discord.Role = self.guild.get_role(value)
            else:
                self.options[key]: int = value

        data = InteractionData(interaction_token=self.token, interaction_id=self.id, application_id=self.application)
        self.http = HttpClient(http=self.client.http, data=data)

    @staticmethod
    def _get_payload(
            content=None,
            tts: bool = False,
            embed=None,
            hidden: bool = False,
            allowed_mentions=None,
            components=None
    ) -> dict:

        payload = {}
        if content:
            payload['content'] = content
        if tts:
            payload['tts'] = tts
        if embed:
            payload['embeds'] = [embed]
        if allowed_mentions:
            payload['allowed_mentions'] = allowed_mentions
        if hidden:
            payload['flags'] = 1 << 6
        if components:
            payload['components'] = components
        return payload

    async def defer(self, hidden: bool = False):
        base = {"type": 5}
        if hidden:
            base["data"] = {"flags": 64}

        await self.http.post_defer_response(payload=base)
        self.deferred = True
        return

    async def send(
            self,
            content=None,
            *,
            tts: bool = False,
            embed: discord.Embed = None,
            file: discord.File = None,
            files: List[discord.File] = None,
            hidden: bool = False,
            allowed_mentions: discord.AllowedMentions = None,
            components: List[Union[ActionRow, Button, Selection]] = None
    ):
        if file is not None and files is not None:
            raise

        content = str(content) if content is not None else None
        if embed is not None:
            embed = embed.to_dict()
        if file:
            files = [file]
        if components is not None:
            components = [i.to_all_dict() if isinstance(i, ActionRow) else i.to_dict() for i in components]

        allowed_mentions = _allowed_mentions(self._state, allowed_mentions)
        payload = self._get_payload(
            content=content,
            embed=embed,
            tts=tts,
            hidden=hidden,
            allowed_mentions=allowed_mentions,
            components=components,
        )

        if files:
            form = _files_to_form(files=files, payload=payload)
        else:
            form = None

        if not self.responded:
            if files:
                await self.defer(hidden=hidden)

            if self.deferred:
                resp = await self.http.edit_initial_response(payload=payload, form=form, files=files)
            else:
                await self.http.post_initial_response(payload=payload)
                resp = await self.http.get_initial_response()
            self.responded = True
        else:
            resp = await self.http.post_followup(payload=payload, form=form, files=files)
        ret = self._state.create_message(channel=self.channel, data=resp)

        if files:
            for file in files:
                file.close()
        return ret

    async def edit(
            self,
            message_id="@original",
            content=None,
            *,
            embed: discord.Embed = None,
            file: discord.File = None,
            files: List[discord.File] = None,
            allowed_mentions: discord.AllowedMentions = None,
            components: List[Union[ActionRow, Button, Selection]] = None
    ):
        if file is not None and files is not None:
            raise

        content = str(content) if content is not None else None
        if embed is not None:
            embed = embed.to_dict()
        if file:
            files = [file]
        if components is not None:
            components = [i.to_all_dict() if isinstance(i, ActionRow) else i.to_dict() for i in components]

        allowed_mentions = _allowed_mentions(self._state, allowed_mentions)

        payload = self._get_payload(
            content=content,
            embed=embed,
            allowed_mentions=allowed_mentions,
            components=components,
        )

        if files:
            form = _files_to_form(files=files, payload=payload)
        else:
            form = None

        if message_id == "@original":
            resp = await self.http.edit_initial_response(payload=payload, form=form, files=files)
        else:
            resp = await self.http.edit_followup(message_id, payload=payload, form=form, files=files)
        ret = self._state.create_message(channel=self.channel, data=resp)

        if files:
            for file in files:
                file.close()
        return ret

    async def delete(self, message_id="@original"):
        if message_id == "@original":
            await self.http.delete_initial_response()
        else:
            await self.http.delete_followup(message_id)
        return


class Message(discord.Message):
    def __init__(self, *, state, channel, data):
        super().__init__(state=state, channel=channel, data=data)
        self._state: ConnectionState = self._state
        self.components = from_payload(data.get("components", []))
        self.http = HttpClient(http=self._state.http)

        options = self.content.split()

        if len(options) >= 1:
            self.name = options[0]
        else:
            self.name = None

        if len(options) >= 2:
            self.options = self.content.split()[1:]
        else:
            self.options = []

    @staticmethod
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
            payload['embed'] = embed
        if allowed_mentions:
            payload['allowed_mentions'] = allowed_mentions
        if components:
            payload['components'] = components
        return payload

    async def send(
            self,
            content=None,
            *,
            tts: bool = False,
            embed: discord.Embed = None,
            file: discord.File = None,
            files: List[discord.File] = None,
            allowed_mentions: discord.AllowedMentions = None,
            components: List[Union[ActionRow, Button, Selection]] = None
    ):
        if file is not None and files is not None:
            raise

        content = str(content) if content is not None else None
        if embed is not None:
            embed = embed.to_dict()
        if file:
            files = [file]
        if components is not None:
            components = [i.to_all_dict() if isinstance(i, ActionRow) else i.to_dict() for i in components]
        allowed_mentions = _allowed_mentions(self._state, allowed_mentions)

        payload = self._get_payload(
            content=content,
            tts=tts,
            embed=embed,
            allowed_mentions=allowed_mentions,
            components=components,
        )

        if files:
            form = _files_to_form(files=files, payload=payload)
            resp = await self.http.create_message(form=form, files=files, channel_id=self.channel.id)
        else:
            resp = await self.http.create_message(payload=payload, channel_id=self.channel.id)
        ret = self._state.create_message(channel=self.channel, data=resp)

        if files:
            for file in files:
                file.close()
        return ret
