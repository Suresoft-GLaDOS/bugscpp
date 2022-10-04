"""
Search command.

Clone a repository into the given directory on the host machine.
"""

import os
from typing import List

import git
# from errors import (
#
# )
from message import message
from processor.core.argparser import create_common_parser, create_common_vcs_parser
from processor.core.command import Command, SimpleCommand
from processor.core.data import Project
from taxonomy import Taxonomy


def search_by_tags(tag_list=None):
    # TODO: if tag_lsit is None or empty list?
    taxonomy = Taxonomy()
    search_result = []
    for name in taxonomy:
        if name == "example":
            continue
        for defect in taxonomy[name].defects:
            if all(tag.lower() in defect.tags for tag in tag_list):
                search_result.append(f"{name}#{defect.id}")
                continue
    return search_result


class SearchCommand(SimpleCommand):
    """
    Search command which handles VCS commands based on taxonomy information.
    """

    # _ERROR_MESSAGES: DICT[Type[DppGitError], str] = {
    #     DppNoSuchTagError: "no such tag",
    # }
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
        message.stdout_paragraph(str(search_by_tags(args)))

    @property
    def help(self) -> str:
        return "search defects by tags"
