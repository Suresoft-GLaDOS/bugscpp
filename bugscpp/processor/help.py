"""
Help command.

Display help messages.

WIP
"""
from textwrap import dedent
from typing import List

from message import message
from processor.command_list import CommandList
from processor.core.argparser import create_common_parser
from processor.core.command import SimpleCommand


class HelpCommand(SimpleCommand):
    def __init__(self):
        self.parser = create_common_parser()
        self.parser.usage = "bugcpp.py help"
        self.parser.description = dedent(
            """\
        Display help messages.
        """
        )

    @property
    def help(self) -> str:
        return "Display help messages"

    def run(self, argv: List[str]) -> bool:
        message.stdout_title(
            "Defects4C++: Defect Taxonomies for Automated Debugging Tools"
        )
        message.stdout_title("MIT Licensed, Suresoft Technologies Inc.\n")
        commands = CommandList()
        for k, v in commands.items():
            message.stdout_bullet(v.parser.usage)
            message.stdout_paragraph(f"{v.parser.description}")
        return True
