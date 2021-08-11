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


class Components:
    def __init__(self, components_type: int):
        self.type = components_type


class ActionRow(Components):
    def __init__(self, components: list = None):
        super().__init__(components_type=1)

        self.components: list = components

    def to_dict(self) -> dict:
        return {
            "type": 1,
            "components": self.components
        }

    def to_all_dict(self) -> dict:
        return {
            "type": 1,
            "components": [i.to_dict() for i in self.components]
        }

    def from_dict(self, payload: dict):
        self.components = payload.get("components")
        return self

    def from_payload(self, payload: dict):
        self.components = from_payload(payload.get("components"))
        return self


class Button(Components):
    def __init__(self,
                 style: int = None,
                 label: str = None,
                 emoji: discord.PartialEmoji = None,
                 custom_id: str = None,
                 url: str = None,
                 disabled: bool = None):
        super().__init__(components_type=2)

        self.style = style
        self.label = label
        self.emoji = emoji
        self.custom_id = custom_id
        self.url = url
        self.disabled = disabled

    def to_dict(self) -> dict:
        base = {
            "type": 2,
            "style": self.style
        }

        if self.label is not None:
            base["label"] = self.label
        if self.emoji is not None and isinstance(self.emoji, discord.PartialEmoji):
            base["emoji"] = self.emoji.to_dict()
        elif self.emoji is not None:
            base["emoji"] = self.emoji

        if 0 < self.style < 5 and self.custom_id is not None:
            base["custom_id"] = self.custom_id
        if self.style == 5 and self.url is not None:
            base["url"] = self.url
        if self.disabled is not None:
            base["disabled"] = self.disabled

        return base

    def from_dict(self, payload: dict):
        self.style = payload.get("style")
        self.label = payload.get("label")
        self.emoji = payload.get("emoji")
        self.custom_id = payload.get("custom_id")
        self.url = payload.get("url")
        self.disabled = payload.get("disabled")
        return self


class Selection(Components):
    def __init__(self,
                 custom_id: str = None,
                 options: list = None,
                 placeholder: str = None,
                 min_values: int = None,
                 max_values: int = None):
        super().__init__(components_type=3)

        self.custom_id = custom_id
        self.options = options
        self.placeholder = placeholder
        self.min_values = min_values
        self.max_values = max_values

    def to_dict(self) -> dict:
        base = {
            "type": 3,
            "custom_id": self.custom_id,
            "options": self.options
        }
        if self.placeholder is not None:
            base["placeholder"] = self.placeholder
        if self.min_values is not None:
            base["min_values"] = self.min_values
        if self.max_values is not None:
            base["max_values"] = self.max_values

        return base

    def from_dict(self, payload: dict):
        self.custom_id = payload.get("custom_id")
        self.options = payload.get("options")
        self.placeholder = payload.get("placeholder")
        self.min_values = payload.get("min_values")
        self.max_values = payload.get("max_values")
        return self


def from_payload(payload: dict) -> list:
    components = []

    for i in payload:
        if i.get("type") == 1:
            components.append(ActionRow().from_payload(i))
        elif i.get("type") == 2:
            components.append(Button().from_dict(i))
        elif i.get("type") == 3:
            components.append(Selection().from_dict(i))
    return components
