import asyncio


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

        self.interaction: bool = kwargs.get('interaction', True)
        self.message: bool = kwargs.get('message', True)


def command(name=None, cls=None, **attrs):
    if cls is None:
        cls = Command

    def decorator(func):
        return cls(func, name=name, **attrs)
    return decorator