import asyncio

from typing import List


class Command:
    def __init__(self, func, **kwargs):
        if not asyncio.iscoroutinefunction(func):
            raise TypeError('Callback must be a coroutine.')

        self.name = name = kwargs.get('name') or func.__name__
        if not isinstance(name, str):
            raise TypeError('Name of a command must be a string.')

        self.callback = func
        self.aliases: list = kwargs.get('aliases', [])

        self.permission: int = kwargs.get('permission', 4)
        self.option_name: list = kwargs.get("option_name", [])

        self.interaction: bool = kwargs.get('interaction', True)
        self.message: bool = kwargs.get('message', True)


def command(
        name: str = None,
        cls: classmethod = None,
        aliases: List[str] = None,
        permission: int = 4,
        interaction: bool = True,
        message: bool = True,
        option_name: List[str] = None
):
    if aliases is None:
        aliases = []

    if cls is None:
        cls = Command

    def decorator(func):
        return cls(
            func,
            name=name,
            aliases=aliases,
            permission=permission,
            interaction=interaction,
            message=message,
            option_name=option_name
        )

    return decorator
