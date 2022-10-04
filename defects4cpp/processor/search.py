"""
Search command.

Clone a repository into the given directory on the host machine.
"""
from typing import List

from errors import DppNoSuchTagError
from message import message
from processor.core.argparser import create_common_parser
from processor.core.command import SimpleCommand
from taxonomy import Taxonomy

try:
    from functools import cached_property
except ImportError:
    cached_property = property


def search_by_tags(tag_list=None):
    if tag_list is None:
        return None
    taxonomy = Taxonomy()
    search_result = []
    for name in taxonomy:
        if name == "example":
            continue
        for defect in taxonomy[name].defects:
            if all(tag.lower() in defect.tags for tag in tag_list):
                search_result.append(f"{name}#{defect.id}")
    return search_result


class SearchCommand(SimpleCommand):
    """
    Search command which handles VCS commands based on taxonomy information.
    """

    def run(self, argv: List[str]) -> bool:
        pass

    def __init__(self):
        self.parser = create_common_parser()
        self.parser.add_argument("tags", nargs="+", help="Tags to search")
        self.parser.usage = "d++.py search TAGS"

    def __call__(self, argv: List[str]):
        """

        Parameters
        ----------
        argv : List[str]
            Tag lists

        Returns
        -------
        None
        """
        args = self.parser.parse_args(argv)
        args = [arg.lower() for arg in args.tags]
        args = [arg.replace("_", "-") for arg in args]
        no_such_tags = [tag for tag in args if tag not in self.all_tags]
        if no_such_tags:
            raise DppNoSuchTagError(no_such_tags)
        message.stdout_stream(str(" \n".join(search_by_tags(args))) + "\n")

    @property
    def help(self) -> str:
        return "search defects by tags"

    @cached_property
    def all_tags(self):
        taxonomy = Taxonomy()
        tags = set()
        for name in taxonomy:
            if name == "example":
                continue
            for defect in taxonomy[name].defects:
                tags.update(defect.tags)
        return sorted(tags)
