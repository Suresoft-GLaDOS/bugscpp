"""
Define data types used within processor module.

"""
import json
from dataclasses import asdict, dataclass, field, fields
from os import getcwd
from pathlib import Path, PurePosixPath
from typing import Tuple, Union

from config import config
from errors import DppArgparseConfigCorruptedError, DppArgparseFileNotFoundError, DppArgparseInvalidConfigError
from taxonomy import MetaData, Taxonomy

NAMESPACE_ATTR_INDEX = "index"
NAMESPACE_ATTR_BUGGY = "buggy"
NAMESPACE_ATTR_WORKSPACE = "workspace"
NAMESPACE_ATTR_PATH = "path"
NAMESPACE_ATTR_PATH_CONFIG_NAME = ".defects4cpp.json"
NAMESPACE_ATTR_METADATA = "metadata"
NAMESPACE_ATTR_METADATA_BASE = "metadata_base"


@dataclass
class Worktree:
    """
    Dataclass to manage host and container directory structure.

    """

    project_name: str
    """The name of the defect taxonomy."""
    index: int
    """The index number of taxonomy."""
    buggy: bool = field(default=False)
    """True if the project is configured as buggy, otherwise False."""
    workspace: str = field(default=getcwd())
    """The workspace path string."""

    @property
    def base(self) -> Path:
        """Return base path which will be used to test and build defect taxonomies"""
        return Path(f"{self.workspace}/{self.project_name}")

    @property
    def suffix(self) -> Path:
        """Return suffix path which is appended to base path"""
        return Path(f"{'buggy' if self.buggy else 'fixed'}-{self.index}")

    @property
    def host(self) -> Path:
        """Return path from which is mounted"""
        return self.base / self.suffix

    @property
    def container(self) -> PurePosixPath:
        """Return path to which is mounted inside docker"""
        return PurePosixPath(config.DPP_DOCKER_HOME)

    def __post_init__(self):
        for f in fields(self):
            value = getattr(self, f.name)
            if not value:
                setattr(self, f.name, f.default)


class Project:
    """
    Load and save project from path.

    """

    @staticmethod
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
            with open(Path(project_dir) / NAMESPACE_ATTR_PATH_CONFIG_NAME, "r") as fp:
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

    @staticmethod
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
        config_file = Path(worktree.host) / NAMESPACE_ATTR_PATH_CONFIG_NAME
        if config_file.exists():
            return

        try:
            with open(config_file, "w+") as fp:
                json.dump(asdict(worktree), fp)
        except FileNotFoundError as e:
            raise DppArgparseFileNotFoundError(e.filename)
