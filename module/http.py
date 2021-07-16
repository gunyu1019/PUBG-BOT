import discord
from discord.http import Route


class SlashRoute(Route):
    BASE = "https://discord.com/api/v9"


class InteractionData:
    def __init__(self, interaction_token, interaction_id=None, application_id=None):
        self.id = str(interaction_id)
        self.application = str(application_id)
        self.token: str = interaction_token


class HttpClient:
    def __init__(self, http: discord.http.HTTPClient, data: InteractionData = None):
        self.http = http
        self.data = data

    async def post_defer_response(self, payload: dict):
        r = Route("POST", "/interactions/{id}/{token}/callback", id=self.data.id, token=self.data.token)
        data = {"type": 5, "data": payload}
        await self.http.request(r, json=data)

    async def post_initial_response(self, payload: dict):
        r = Route("POST", "/interactions/{id}/{token}/callback", id=self.data.id, token=self.data.token)
        data = {"type": 4, "data": payload}
        return await self.http.request(r, json=data)

    async def post_initial_components_response(self, payload: dict):
        r = Route("POST", "/interactions/{id}/{token}/callback", id=self.data.id, token=self.data.token)
        data = {"type": 7, "data": payload}
        return await self.http.request(r, json=data)

    async def get_initial_response(self):
        r = Route("GET", "/webhooks/{id}/{token}/messages/@original", id=self.data.application, token=self.data.token)
        return await self.http.request(r)

    async def edit_initial_response(self, payload: dict = None, form=None, files=None):
        if files is not None or form is not None:
            return await self.edit_followup("@original", form=form, files=files)
        return await self.edit_followup("@original", payload=payload)

    async def delete_initial_response(self):
        await self.delete_followup("@original")

    async def post_followup(self, payload: dict = None, form=None, files=None):
        r = Route("POST", "/webhooks/{id}/{token}", id=self.data.application, token=self.data.token)
        if files is not None or form is not None:
            return await self.http.request(r, form=form, files=files)
        return await self.http.request(r, json=payload)

    async def edit_followup(self, message_id, payload: dict = None, form=None, files=None):
        r = Route(
            "PATCH", "/webhooks/{id}/{token}/messages/{message_id}",
            id=self.data.application, token=self.data.token, message_id=message_id
        )
        if files is not None or form is not None:
            return await self.http.request(r, form=form, files=files)
        return await self.http.request(r, json=payload)

    async def delete_followup(self, message_id):
        r = Route(
            "DELETE", "/webhooks/{id}/{token}/messages/{message_id}",
            id=self.data.application, token=self.data.token, message_id=message_id
        )
        await self.http.request(r)

    async def create_message(self, channel_id, payload: dict = None, form=None, files=None):
        r = Route('POST', '/channels/{channel_id}/messages', channel_id=channel_id)
        if files is not None or form is not None:
            return await self.http.request(r, form=form, files=files)
        return await self.http.request(r, json=payload)

    async def edit_message(self, channel_id, message_id, payload: dict = None, form=None, files=None):
        r = Route('PATCH', '/channels/{channel_id}/messages/{message_id}', channel_id=channel_id, message_id=message_id)
        if files is not None or form is not None:
            return await self.http.request(r, form=form, files=files)
        return await self.http.request(r, json=payload)
