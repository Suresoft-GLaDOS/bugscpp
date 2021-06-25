import argparse
from abc import ABCMeta
from os.path import exists
from typing import List, Tuple

from defects4cpp.taxonomy import MetaData, Taxonomy


class ValidateProject(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        t = Taxonomy()
        if values not in t.keys():
            # TODO:
            raise KeyError("")
        setattr(namespace, self.dest, t[values])


class ValidateCheckout(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        # TODO: ?
        assert exists(values)
        setattr(namespace, self.dest, values)


class ParserBase(metaclass=ABCMeta):
    pass


class BuildParser(ParserBase):
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
            "-n", "--no", type=int, required=True, help="specified bug number"
        )
        self.parser.add_argument(
            "-b",
            "--buggy",
            default="fixed",
            const="fixed",
            nargs="?",
            choices=["buggy", "fixed"],
            help="whether buggy version or not",
        )
        # TODO: ?
        # self.parser.add_argument("checkout", action=ValidateCheckout)

    def __call__(self, argv: List[str]) -> Tuple[MetaData, int, bool]:
        args = self.parser.parse_args(argv)
        metadata: MetaData = args.project
        index: int = args.no
        # TODO: should be enum
        buggy = True if args.buggy == "buggy" else False
        try:
            defect = metadata.defects[index]
        except IndexError:
            # TODO:
            raise IndexError("")
        return (metadata, index, buggy)
