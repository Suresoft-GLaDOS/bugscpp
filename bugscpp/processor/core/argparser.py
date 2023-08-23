"""
Provide common argparsers

Utility functions to parse command line arguments and argparsers used across modules are defined.
"""
import argparse
from pathlib import Path

from taxonomy import Taxonomy

from .data import NAMESPACE_ATTR_BUGGY, NAMESPACE_ATTR_INDEX, NAMESPACE_ATTR_WORKSPACE
from .validator.common_command import ValidateCompilationDBTool
from .validator.project_command import (ValidateBuggy, ValidateEnviron, ValidateIndex, ValidateProjectPath,
                                        ValidateTaxonomy, ValidateWorkspace)


def create_common_parser() -> argparse.ArgumentParser:
    """
    Returns argparse.ArgumentParser that parses common options.

    Returns
    -------
    argparse.ArgumentParser
        Return argparse.ArgumentParser that parses common options.
    """
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        "--compilation_db_tool",
        type=str,
        help="command to capture build. (default: bear)",
        action=ValidateCompilationDBTool,
    )
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
        choices=[name for name in t],
        action=ValidateTaxonomy,
    )
    parser.add_argument(
        NAMESPACE_ATTR_INDEX,
        type=int,
        help="index of defects.",
        action=ValidateIndex,
    )
    parser.add_argument(
        "-b",
        "--buggy",
        dest=NAMESPACE_ATTR_BUGGY,
        help="checkout a buggy commit.",
        nargs=0,
        action=ValidateBuggy,
    )
    # 'dest', 'root', 'workspace', 'checkout_directory'...
    parser.add_argument(
        "-t",
        "--target",
        dest=NAMESPACE_ATTR_WORKSPACE,
        type=str,
        help="checkout to the specified directory instead of the current directory.",
        action=ValidateWorkspace,
    )
    parser.add_argument(
        "-s",
        "--source-only",
        dest="source_only",
        help="checkout source code only.",
        action="store_true",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        dest="verbose",
        help="verbose mode",
        action="store_true",
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
    parser.add_argument(
        "--rebuild-image",
        dest="rebuild_image",
        help="rebuild docker image.",
        action="store_true",
    )
    parser.add_argument(
        "--env",
        type=str,
        dest="env",
        nargs=1,
        help="set 'key=value' environment variables within container. (can be used multiple times)",
        action=ValidateEnviron,
    )
    parser.add_argument(
        "-j", "--jobs", type=int, help="number of jobs to run in parallel.", default=1
    )
    return parser
