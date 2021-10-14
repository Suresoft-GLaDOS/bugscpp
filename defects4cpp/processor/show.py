"""
Show command.

Display detailed information about defect taxonomy.

WIP
"""
import message
from processor.core import SimpleCommand
from taxonomy import Taxonomy


class ShowCommandParser:
    def __init__(self):
        self.value = None

    def __get__(self, instance, owner):
        return self.value

    def __set__(self, instance, value):
        self.value = float(value)


class ShowCommand(SimpleCommand):
    parser = ShowCommandParser()

    @property
    def help(self) -> str:
        return "Display defect taxonomies status"

    def run(self, *args, **kwargs) -> bool:
        message.kind("=== Taxonomy Project Lists ===")
        t = Taxonomy()
        for key, value in t.items():
            message.info(f"[{key}], # of taxonomies: {len(value.defects)}")
            message.info2(f"URL: {value.info.url}")
            message.info2(f"Description: {value.info.description}")
        return True
