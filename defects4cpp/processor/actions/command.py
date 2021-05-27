import subprocess


class AbstractAction():
    def run(self):
        pass


class CommandAction(AbstractAction):
    def __init__(self, commands):
        self._COMMANDS = commands

    def run(self):
        for c in self._COMMANDS:
            print("RUN: ", c)
            if subprocess.call(c) != 0:
                return False
        return True
