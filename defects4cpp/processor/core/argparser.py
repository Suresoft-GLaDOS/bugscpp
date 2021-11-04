"""
Provide common argparsers

Utility functions to parse command line arguments and argparsers used across modules are defined.
"""
import argparse
import json
from dataclasses import asdict
from pathlib import Path
from typing import Tuple, Union

from errors import (DppArgparseConfigCorruptedError, DppArgparseDefectIndexError, DppArgparseFileNotFoundError,
                    DppArgparseInvalidConfigError, DppArgparseNotProjectDirectory, DppArgparseTaxonomyNotFoundError)
from processor.core.docker import Worktree
from taxonomy import MetaData, Taxonomy

_NAMESPACE_ATTR_INDEX = "index"
_NAMESPACE_ATTR_BUGGY = "buggy"
_NAMESPACE_ATTR_WORKSPACE = "workspace"
_NAMESPACE_ATTR_PATH = "path"
_NAMESPACE_ATTR_PATH_CONFIG_NAME = ".defects4cpp.json"
_NAMESPACE_ATTR_METADATA = "metadata"


def _set_worktree(obj: argparse.Namespace):
    def worktree(self: argparse.Namespace) -> Worktree:
        return Worktree(self.metadata.name, self.index, self.buggy, self.workspace)

    cls = type(obj)
    if not hasattr(cls, worktree.__name__):
        new_cls = type(cls.__name__, (cls,), {})
        obj.__class__ = new_cls
        setattr(new_cls, worktree.__name__, property(worktree))


def read_config(project_dir: Union[str, Path]) -> Tuple[MetaData, Worktree]:
    """
    Read config file and return parsed options.

    Parameters
    ----------
    project_dir : Union[str, Path]
        Path to where defect taxonomy is located.

    Returns
    -------
    Tuple[taxonomy.MetaData, docker.Worktree]
        Return a tuple of metadata and worktree information.
    """
    try:
        with open(Path(project_dir) / _NAMESPACE_ATTR_PATH_CONFIG_NAME, "r") as fp:
            data = json.load(fp)
    except FileNotFoundError as e:
        raise DppArgparseFileNotFoundError(e.filename)
    except json.JSONDecodeError:
        raise DppArgparseInvalidConfigError()

    try:
        worktree = Worktree(**data)
    except TypeError:
        raise DppArgparseConfigCorruptedError(data)

    t = Taxonomy()
    return t[worktree.project_name], worktree


def write_config(worktree: Worktree) -> None:
    """
    Write config file to the directory.

    Parameters
    ----------
    worktree : taxonomy.Worktree
        Worktree

    Returns
    -------
    None
    """
    config_file = Path(worktree.host) / _NAMESPACE_ATTR_PATH_CONFIG_NAME
    if config_file.exists():
        return

    try:
        with open(config_file, "w+") as fp:
            json.dump(asdict(worktree), fp)
    except FileNotFoundError as e:
        raise DppArgparseFileNotFoundError(e.filename)


class ValidateProjectPath(argparse.Action):
    """
    Validator for project path argument.
    """

    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: Path,
        option_string=None,
    ):
        p = values.absolute()
        if not p.exists() or not (p / _NAMESPACE_ATTR_PATH_CONFIG_NAME).exists():
            raise DppArgparseNotProjectDirectory(values)
        metadata, worktree = read_config(p)

        _set_worktree(namespace)
        setattr(namespace, _NAMESPACE_ATTR_METADATA, metadata)
        setattr(namespace, _NAMESPACE_ATTR_INDEX, worktree.index)
        setattr(namespace, _NAMESPACE_ATTR_BUGGY, worktree.buggy)
        setattr(namespace, _NAMESPACE_ATTR_WORKSPACE, worktree.workspace)
        setattr(namespace, _NAMESPACE_ATTR_PATH, str(p))


class ValidateTaxonomy(argparse.Action):
    """
    Validator for taxonomy argument.
    """

    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: str,
        option_string=None,
    ):
        t = Taxonomy()
        # Probably redundant to check 'values' exists in keys.
        if values not in t.keys():
            raise DppArgparseTaxonomyNotFoundError(values)

        _set_worktree(namespace)
        setattr(namespace, _NAMESPACE_ATTR_METADATA, t[values])


class ValidateIndex(argparse.Action):
    """
    Validator for index argument.
    """

    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: int,
        option_string=None,
    ):
        metadata = namespace.metadata
        if values < 1 or len(metadata.defects) < values:
            raise DppArgparseDefectIndexError(values)

        _set_worktree(namespace)
        setattr(namespace, self.dest, values)


class ValidateBuggy(argparse.Action):
    """
    Validator for buggy argument.
    """

    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values,
        option_string=None,
    ):
        _set_worktree(namespace)
        setattr(namespace, self.dest, True)


class ValidateWorkspace(argparse.Action):
    """
    Validator for workspace argument.
    """

    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: str,
        option_string=None,
    ):
        _set_worktree(namespace)
        setattr(namespace, self.dest, values)


def create_common_parser() -> argparse.ArgumentParser:
    """
    Returns argparse.ArgumentParser that parses common options.

    Returns
    -------
    argparse.ArgumentParser
        Return argparse.ArgumentParser that parses common options.
    """
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    return parser


def create_common_vcs_parser() -> argparse.ArgumentParser:
    """
    Create an argparse.ArgumentParser that parses common vcs options.

    Returns
    -------
    argparse.ArgumentParser
        Return argparse.ArgumentParser that parses common taxonomy options.
        Its namespace also provides 'worktree' attribute for convenience.
    """
    parser = create_common_parser()
    t = Taxonomy()
    parser.add_argument(
        "project",
        type=lambda s: s.lower(),
        help="name of defect taxonomy.",
        choices=[name for name in t.keys()],
        action=ValidateTaxonomy,
    )
    parser.add_argument(
        _NAMESPACE_ATTR_INDEX,
        type=int,
        help="index of defects.",
        action=ValidateIndex,
    )
    parser.add_argument(
        "-b",
        "--buggy",
        dest=_NAMESPACE_ATTR_BUGGY,
        help="checkout a buggy commit.",
        nargs=0,
        action=ValidateBuggy,
    )
    # 'dest', 'root', 'workspace', 'checkout_directory'...
    parser.add_argument(
        "-t",
        "--target",
        dest=_NAMESPACE_ATTR_WORKSPACE,
        type=str,
        help="checkout to the specified directory instead of the current directory.",
        action=ValidateWorkspace,
    )
    return parser


def create_common_project_parser() -> argparse.ArgumentParser:
    """
    Create an argparse.ArgumentParser that parses common project options.
    'path' is path to the existing directory with defects4cpp configuration which has been already checkout.

    Returns
    -------
    argparse.ArgumentParser
        Return argparse.ArgumentParser that parses common project options.
    """
    parser = create_common_parser()
    parser.add_argument(
        "path",
        type=Path,
        help="path to checkout directory.",
        action=ValidateProjectPath,
    )
    parser.add_argument(
        "-v",
        "--verbose",
        dest="verbose",
        help="redirect output to stdout.",
        action="store_true",
    )
    parser.add_argument(
        "--coverage",
        dest="coverage",
        help="set coverage flags.",
        action="store_true",
    )
    return parser
