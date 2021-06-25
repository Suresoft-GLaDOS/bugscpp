import defects4cpp.lib.message as message
from defects4cpp.processor.core.argparser import ParserBase
from defects4cpp.processor.core.command import SimpleCommand


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
        message("HELP")
        return True
