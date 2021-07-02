from typing import List

import message
import processor
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

    def run(self, argv: List[str]) -> bool:
        message.kind("Defects4C++: Defected Taxonomies for Automated Debugging Tools")
        message.kind("MIT Licensed, Suresoft Technologies Inc.")
        message.blank()
        message.kind("Usage:")
        message.command("    d++ COMMAND [OPTIONS]")
        message.blank()
        message.kind("COMMAND:")
        commands = processor.CommandList()
        for k, v in commands.items():
            message.command(f"    {k:<10}\t{v.help}")
        message.blank()
        return True
