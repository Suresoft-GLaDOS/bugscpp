import argparse
from os import getcwd

import errors
from processor.core.docker import Worktree
from taxonomy import MetaData, Taxonomy


def _get_worktree_attr(namespace: argparse.Namespace) -> Worktree:
    if not hasattr(namespace, "worktree"):
        setattr(namespace, "worktree", Worktree())
    return getattr(namespace, "worktree")


class ValidateProject(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        t = Taxonomy()
        if values not in t.keys():
            raise errors.DppTaxonomyNotFoundError(values)
        worktree = _get_worktree_attr(namespace)
        worktree._name = t[values].name
        setattr(namespace, self.dest, t[values])


class ValidateIndex(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        try:
            metadata: MetaData = namespace.metadata
        except AttributeError:
            raise errors.DppCommandLineInternalError(__class__.__name__)

        if 0 < len(metadata.defects) < values:
            raise errors.DppDefectIndexError(values)

        worktree = _get_worktree_attr(namespace)
        worktree._index = values
        setattr(namespace, self.dest, values)


class ValidateBuggy(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        worktree = _get_worktree_attr(namespace)
        worktree._buggy = True
        setattr(namespace, self.dest, True)


class ValidateWorkspace(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        worktree = _get_worktree_attr(namespace)
        worktree._workspace = values
        setattr(namespace, self.dest, values)


def create_taxonomy_parser():
    """
    Returns argparse.ArgumentParser that parses common taxonomy options.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p",
        "--project",
        required=True,
        help="specified project",
        dest="metadata",
        action=ValidateProject,
    )
    parser.add_argument(
        "-n",
        "--no",
        type=int,
        required=True,
        help="specified bug number",
        dest="index",
        action=ValidateIndex,
    )
    parser.add_argument(
        "-b",
        "--buggy",
        dest="buggy",
        help="whether buggy version or not",
        nargs=0,
        action=ValidateBuggy,
    )
    # 'dest', 'root', 'workspace', 'checkout_directory'...
    parser.add_argument(
        "-t",
        "--target",
        dest="workspace",
        type=str,
        default=f"{getcwd()}",
        help="checkout directory",
        action=ValidateWorkspace,
    )
    parser.add_argument(
        "-q",
        "--quiet",
        dest="quiet",
        help="suppress stream output of container",
        action="store_true",
    )
    return parser
