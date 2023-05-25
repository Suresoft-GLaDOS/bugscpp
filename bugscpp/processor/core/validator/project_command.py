import argparse
from pathlib import Path
from typing import List

from errors import (DppArgparseDefectIndexError, DppArgparseInvalidEnvironment, DppArgparseNotProjectDirectory,
                    DppArgparseTaxonomyNotFoundError)
from processor.core.data import (NAMESPACE_ATTR_BUGGY, NAMESPACE_ATTR_INDEX, NAMESPACE_ATTR_METADATA,
                                 NAMESPACE_ATTR_METADATA_BASE, NAMESPACE_ATTR_PATH, NAMESPACE_ATTR_PATH_CONFIG_NAME,
                                 NAMESPACE_ATTR_WORKSPACE, Project, Worktree)
from taxonomy import Taxonomy


def _set_worktree(obj: argparse.Namespace):
    def worktree(self: argparse.Namespace) -> Worktree:
        return Worktree(self.metadata.name, self.index, self.buggy, self.workspace)

    cls = type(obj)
    if not hasattr(cls, worktree.__name__):
        new_cls = type(cls.__name__, (cls,), {})
        obj.__class__ = new_cls
        setattr(new_cls, worktree.__name__, property(worktree))


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
        if not p.exists() or not (p / NAMESPACE_ATTR_PATH_CONFIG_NAME).exists():
            raise DppArgparseNotProjectDirectory(values)
        metadata, worktree = Project.read_config(p)

        _set_worktree(namespace)
        setattr(namespace, NAMESPACE_ATTR_METADATA, metadata)
        setattr(namespace, NAMESPACE_ATTR_INDEX, worktree.index)
        setattr(namespace, NAMESPACE_ATTR_BUGGY, worktree.buggy)
        setattr(namespace, NAMESPACE_ATTR_WORKSPACE, worktree.workspace)
        setattr(namespace, NAMESPACE_ATTR_PATH, str(p))


class ValidateEnviron(argparse.Action):
    """
    Validator for env argument.
    """

    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: List[str],
        option_string=None,
    ):
        if not getattr(namespace, self.dest, None):
            setattr(namespace, self.dest, {})
        dest = getattr(namespace, self.dest)
        string = values[0]
        try:
            string = string.strip('"').strip("'")
            key, value = string.split("=")
            if not key:
                raise ValueError
        except ValueError:
            raise DppArgparseInvalidEnvironment(values[0])
        dest[key] = value


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
        if values not in t:
            raise DppArgparseTaxonomyNotFoundError(values)

        _set_worktree(namespace)
        setattr(namespace, NAMESPACE_ATTR_METADATA, t[values])
        setattr(namespace, NAMESPACE_ATTR_METADATA_BASE, t.base)


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
