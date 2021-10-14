"""
Manage commands associated with docker SDK module.

Do not use docker SDK directly, instead use Docker class.
"""
import sys
from dataclasses import dataclass, field
from os import getcwd
from pathlib import Path, PurePosixPath
from typing import Dict, Optional, cast

import docker
import docker.errors
import message
from config.env import DPP_DOCKER_HOME, DPP_DOCKER_USER
from docker import DockerClient
from docker.models.containers import Container, ExecResult
from docker.models.images import Image


def _cast_image(image) -> Image:
    """
    Helper function to get a correct type
    """
    return cast(Image, image)


def _cast_container(container) -> Container:
    """
    Helper function to get a correct type
    """
    return cast(Container, container)


def _build_image(client, tag, path) -> Image:
    """
    Helper function to get a correct type
    """
    return client.images.build(rm=True, tag=tag, path=path)[0]


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
        return Path(f"{'buggy' if self.buggy else 'fixed'}#{self.index}")

    @property
    def host(self) -> Path:
        """Return path from which is mounted"""
        return self.base / self.suffix

    @property
    def container(self) -> PurePosixPath:
        """Return path to which is mounted inside docker"""
        return PurePosixPath(DPP_DOCKER_HOME)


class _Client:
    def __get__(self, instance, owner) -> DockerClient:
        if getattr(owner, "_client", None) is None:
            try:
                setattr(owner, "_client", docker.from_env())
            except docker.errors.DockerException:
                message.warning(
                    "Could not get response from docker. Is your docker-daemon running?"
                )
                sys.exit(0)
        return getattr(owner, "_client")


class Docker:
    """
    Provide docker SDK methods along with context manager.
    It is highly recommend to use this via `with` statement.

    Examples
    --------
    >>> with Docker("/path/to/Dockerfile", my_worktree) as docker:
    ...     docker.send("echo 'Hello, world!'")

    Notes
    -----
    Host machine must be running docker daemon in background.
    """

    client = _Client()
    """Docker SDK client."""

    def __init__(self, dockerfile: str, worktree: Worktree):
        self._dockerfile = dockerfile
        # Assumes that the name of its parent directory is the same with that of the target.
        tag = Path(dockerfile).parent.name
        self._name: str = f"{tag}-dpp-generated-container"
        self._tag: str = f"{tag}/dppgen"
        self._volume: Dict[str, Dict] = {
            str(worktree.host): {"bind": str(worktree.container), "mode": "rw"}
        }
        self._working_dir: str = str(worktree.container)
        self._image: Optional[Image] = None
        self._container: Optional[Container] = None

    @property
    def image(self) -> Image:
        """Docker SDK Image."""
        if not self._image:
            try:
                self._image = _cast_image(self.client.images.get(self._tag))
            except docker.errors.ImageNotFound:
                message.info2(
                    f"Creating a new docker image for {Path(self._dockerfile).parent.name}"
                )
                self._image = _build_image(
                    self.client, self._tag, str(Path(self._dockerfile).parent)
                )
            else:
                pass
        return self._image

    def __enter__(self):
        message.info(f"Starting container")
        self._container = _cast_container(
            self.client.containers.run(
                self.image,
                auto_remove=True,
                detach=True,
                stdin_open=True,
                volumes=self._volume,
                name=self._name,
                command="/bin/sh",
                user=DPP_DOCKER_USER,
                working_dir=self._working_dir,
            )
        )
        return self

    def __exit__(self, type, value, traceback):
        message.info(f"Closing container")
        self._container.stop()

    def send(self, command: str, stream=True) -> ExecResult:
        """
        Send a single line command to the running container.
        """
        return self._container.exec_run(command, stream=stream)
