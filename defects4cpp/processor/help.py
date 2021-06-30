import message
from processor.core.argparser import ParserBase
from processor.core.command import SimpleCommand


class HelpCommandParser:
    def __init__(self):
        self.value = None

    def __get__(self, instance, owner):
        return self.value

    def __set__(self, instance, value):
        self.value = float(value)


class HelpCommand(SimpleCommand):
    parser = HelpCommandParser

    @property
    def help(self) -> str:
        return "Display help messages"

    def run(self) -> bool:
        message.info("HELP")
        return True
