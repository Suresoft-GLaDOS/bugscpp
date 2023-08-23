"""
Show command.

Display detailed information about defect taxonomy.

WIP
"""
from textwrap import dedent

from message import message
from processor.core.argparser import create_common_parser
from processor.core.command import SimpleCommand
from taxonomy import Taxonomy


class ShowCommand(SimpleCommand):
    def __init__(self):
        self.parser = create_common_parser()
        self.parser.usage = "bugcpp.py show [PROJECT]"
        self.parser.description = dedent(
            """\
        Display defect taxonomy in detail.
        """
        )

    @property
    def help(self) -> str:
        return "Display defect taxonomies status"

    def run(self, *args, **kwargs) -> bool:
        message.stdout_title("Taxonomy Project Lists\n")
        t = Taxonomy()
        for key, value in t.items():
            # hide example
            if key == "example":
                continue
            message.stdout_bullet(f"[{key}], # of taxonomies: {len(value.defects)}")
            message.stdout_paragraph(f"URL: {value.info.url}\n")
            message.stdout_paragraph(f"Description: {value.info.description}")
        return True
