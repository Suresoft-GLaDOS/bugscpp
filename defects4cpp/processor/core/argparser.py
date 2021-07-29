import argparse
import json
from dataclasses import asdict
from os.path import isdir
from pathlib import Path
from typing import Tuple, Union

import errors
from processor.core.docker import Worktree
from taxonomy import MetaData, Taxonomy

_NAMESPACE_ATTR_PATH = "path"
_NAMESPACE_ATTR_PATH_CONFIG_NAME = ".defects4cpp.json"
_NAMESPACE_ATTR_METADATA = "metadata"
_NAMESPACE_ATTR_WORKTREE = "worktree"


def read_config(project_dir: Union[str, Path]) -> Tuple[MetaData, Worktree]:
    """
    Read config file and return parsed options.
    """
    try:
        with open(Path(project_dir) / _NAMESPACE_ATTR_PATH_CONFIG_NAME, "r") as fp:
            data = json.load(fp)
    except FileNotFoundError as e:
        raise errors.DppFileNotFoundError(e.filename)
    except json.JSONDecodeError:
        raise errors.DppInvalidConfigError()

    try:
        worktree = Worktree(**data)
    except TypeError:
        raise errors.DppConfigCorruptedError(data)

    t = Taxonomy()
    return t[worktree.project_name], worktree


def write_config(worktree: Worktree) -> None:
    """
    Write config file to the directory.
    """
    config_file = Path(worktree.host) / _NAMESPACE_ATTR_PATH_CONFIG_NAME
    if config_file.exists():
        return

    try:
        with open(config_file, "w+") as fp:
            json.dump(asdict(worktree), fp)
    except FileNotFoundError as e:
        raise errors.DppFileNotFoundError(e.filename)


class ValidateProjectPath(argparse.Action):
    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: Path,
        option_string=None,
    ):
        p = values.absolute()
        if not p.exists() or not (p / _NAMESPACE_ATTR_PATH_CONFIG_NAME).exists():
            raise errors.DppTaxonomyNotProjectDirectory(values)
        metadata, worktree = read_config(p)

        setattr(namespace, _NAMESPACE_ATTR_METADATA, metadata)
        setattr(namespace, _NAMESPACE_ATTR_WORKTREE, worktree)
        setattr(namespace, _NAMESPACE_ATTR_PATH, str(p))


class ValidateTaxonomy(argparse.Action):
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
            raise errors.DppTaxonomyNotFoundError(values)
        setattr(namespace, _NAMESPACE_ATTR_METADATA, t[values])


class ValidateIndex(argparse.Action):
    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: int,
        option_string=None,
    ):
        metadata = namespace.metadata
        if 0 < len(metadata.defects) < values:
            raise errors.DppDefectIndexError(values)

        setattr(namespace, _NAMESPACE_ATTR_WORKTREE, Worktree(metadata.name, values))
        setattr(namespace, self.dest, values)


class ValidateBuggy(argparse.Action):
    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values,
        option_string=None,
    ):
        worktree = getattr(namespace, _NAMESPACE_ATTR_WORKTREE, None)
        if worktree:
            worktree.buggy = True
        setattr(namespace, self.dest, True)


class ValidateWorkspace(argparse.Action):
    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: str,
        option_string=None,
    ):
        worktree = getattr(namespace, _NAMESPACE_ATTR_WORKTREE, None)
        if worktree:
            worktree.workspace = values
        setattr(namespace, self.dest, values)


class ProjectType:
    def __init__(self, value: str):
        self.value: str = value

    def __eq__(self, other: str):
        if other == "PATH":
            return isdir(self.value)
        return self.value == other


def create_common_parser() -> argparse.ArgumentParser:
    """
    Returns argparse.ArgumentParser that parses common options.
    """
    parser = argparse.ArgumentParser()
    return parser


def create_common_vcs_parser() -> argparse.ArgumentParser:
    """
    project index [-b|--buggy] [-t|--target] [common options]

    Returns argparse.ArgumentParser that parses common taxonomy options.
    Its namespace also provides 'worktree' attribute for convenience.
    """
    parser = create_common_parser()
    t = Taxonomy()
    parser.add_argument(
        "project",
        type=lambda s: s.lower(),
        choices=[name for name in t.keys()],
        action=ValidateTaxonomy,
    )
    parser.add_argument(
        "index",
        type=int,
        help="index of defects (must be passed if project name is given instead of path)",
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
        help="checkout directory",
        action=ValidateWorkspace,
    )
    return parser


def create_common_project_parser() -> argparse.ArgumentParser:
    """
    path [--coverage] [common options]

    Returns argparse.ArgumentParser that parses common project options.

    'path' is path to the existing directory with defects4cpp configuration which has been already checkout.
    """
    parser = create_common_parser()
    parser.add_argument(
        "path",
        type=Path,
        action=ValidateProjectPath,
    )
    parser.add_argument(
        "-v",
        "--verbose",
        dest="verbose",
        help="stream output to stdout (output will not be written to file)",
        action="store_true",
    )
    parser.add_argument(
        "--coverage",
        dest="coverage",
        help="build with gcov flags",
        action="store_true",
    )
    return parser
