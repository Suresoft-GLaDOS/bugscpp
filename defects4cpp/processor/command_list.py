"""
Controller

There should be no deep logic
"""
from collections.abc import Mapping
from typing import Iterator

from processor.core.command import RegisteredCommands


class CommandList(Mapping):
    _commands = RegisteredCommands()

    def __init__(self, *args, **kwargs):
        pass

    def __getitem__(self, key: str):
        return self._commands[self._keytransform(key)]

    def __iter__(self) -> Iterator:
        return iter(self._commands)

    def __len__(self) -> int:
        return len(self._commands)

    def _keytransform(self, key: str):
        return key
