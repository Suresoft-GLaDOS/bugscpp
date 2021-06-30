from typing import List

from processor.core.command import RegisterCommand


class Action:
    def __init__(self):
        self._commands: List[str] = []
        for command, command_type in RegisterCommand.commands.items():
            self._commands.append(command)
            setattr(self, command, command_type())

    @property
    def commands(self):
        return self._commands
