"""
Controller

There should be no deep logic
"""
from collections.abc import MutableMapping

from processor.core.command import RegisteredCommands


class CommandList(MutableMapping):
    _commands = RegisteredCommands()

    def __init__(self, *args, **kwargs):
        # self.update(dict(*args, **kwargs))
        pass

    def __getitem__(self, key: str):
        return self._commands[self._keytransform(key)]

    def __setitem__(self, key: str, value):
        # self.store[self._keytransform(key)] = value
        raise RuntimeError("set operator is not allowed")

    def __delitem__(self, key: str):
        # del self.store[self._keytransform(key)]
        raise RuntimeError("del operator is not allowed")

    def __iter__(self):
        return iter(self._commands)

    def __len__(self):
        return len(self._commands)

    def _keytransform(self, key: str):
        return key
