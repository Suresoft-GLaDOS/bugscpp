import argparse
from abc import ABCMeta
from dataclasses import dataclass
from os import getcwd
from os.path import exists
from typing import List

from taxonomy import MetaData, Taxonomy


def check_taxonomy_index(namespace):
    pass


class ValidateProject(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        t = Taxonomy()
        if values not in t.keys():
            raise KeyError(f"Taxonomy '{values}' does not exist")
        setattr(namespace, self.dest, t[values])


class ValidateIndex(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        try:
            project: MetaData = namespace.project
        except AttributeError:
            raise AttributeError(
                f"project is not set, but {__class__.__name__} is invoked first"
            )

        if len(project.defects) <= values:
            raise IndexError(f"invalid index '{values}' of defects")

        setattr(namespace, self.dest, values)


class ParserBase(metaclass=ABCMeta):
    pass


@dataclass
class TaxonomyArguments:
    metadata: MetaData
    index: int
    buggy: bool
    root: str


class TaxonomyParser(ParserBase):
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument(
            "-p",
            "--project",
            required=True,
            help="specified project",
            action=ValidateProject,
        )
        self.parser.add_argument(
            "-n",
            "--no",
            type=int,
            required=True,
            help="specified bug number",
            action=ValidateIndex,
        )
        self.parser.add_argument(
            "-b",
            "--buggy",
            dest="buggy",
            help="whether buggy version or not",
            action="store_true",
        )
        # 'dest', 'root', 'workspace', 'checkout_directory'...
        self.parser.add_argument("-t", "--target", type=str, help="checkout directory")

    def __call__(self, argv: List[str]) -> TaxonomyArguments:
        args = self.parser.parse_args(argv)
        metadata: MetaData = args.project
        index: int = args.no
        buggy = True if args.buggy else False
        # TODO: default value
        root = args.target or f"{getcwd()}"
        return TaxonomyArguments(metadata, index - 1, buggy, root)
