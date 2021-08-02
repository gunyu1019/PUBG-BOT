import discord

from typing import Union, Optional
from module.components import ActionRow, Button
from module.interaction import SlashContext, Message, ComponentsContext
from utils.directory import directory


class Help:
    def __init__(
            self,
            ctx: Union[SlashContext, Message],
            client: discord.Client,
    ):
        self.ctx = ctx
        self.client = client

        self.page = None

        self.left_btn = None
        self.right_btn = None
        self.init_button()

    def init_button(self):
        self.left_btn = Button(
            style=1,
            emoji=discord.PartialEmoji(id=868342431177900074, name="bar"),
            custom_id="left_page"
        )
        self.right_btn = Button(
            style=1,
            emoji=discord.PartialEmoji(id=868178845373726790, name="solo"),
            custom_id="right_page"
        )

    @property
    def button(self):
        return [
            self.left_btn,
            self.right_btn
        ]

    @staticmethod
    def check(ctx: Message):
        def check_func(component: ComponentsContext):
            return component.component_type == 2 and ctx.id == component.message.id
        return check_func

    def current_button(self):
        self.init_button()
        return

    async def response(self, b_msg: Message, custom_id: str):
        return

    async def first_page(self):
        return
