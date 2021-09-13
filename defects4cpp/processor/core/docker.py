import sys
from dataclasses import dataclass, field
from os import getcwd
from pathlib import Path, PurePosixPath
from typing import Dict, Optional, cast

import docker
import docker.errors
import message
from config.env import DPP_DOCKER_HOME, DPP_DOCKER_USER
from docker.models.containers import Container, ExecResult
from docker.models.images import Image


def cast_image(image) -> Image:
    """
    Helper function to get a correct type
    """
    return cast(Image, image)


def cast_container(container) -> Container:
    """
    Helper function to get a correct type
    """
    return cast(Container, container)


def build_image(client, tag, path) -> Image:
    """
    Helper function to get a correct type
    """
    return client.images.build(rm=True, tag=tag, path=path)[0]


@dataclass
class Worktree:
    """
    Manages host and container git directory structure.
    """

    project_name: str
    index: int
    buggy: bool = field(default=False)
    workspace: str = field(default=getcwd())

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


class Docker:
    """
    Docker RAII
    Host machine must be running docker daemon in background.
    """

    def __init__(self, dockerfile: str, worktree: Worktree):
        self.dockerfile = dockerfile
        # Assumes that the name of its parent directory is the same with that of the target.
        tag = Path(dockerfile).parent.name
        self.name: str = f"{tag}-dpp-generated-container"
        self.tag: str = f"{tag}/dppgen"
        self.volume: Dict[str, Dict] = {
            str(worktree.host): {"bind": str(worktree.container), "mode": "rw"}
        }
        self.working_dir: str = str(worktree.container)

        self._image: Optional[Image] = None
        self._container: Optional[Container] = None

    @property
    def client(self):
        if getattr(Docker, "_client", None) is None:
            try:
                Docker._client = docker.from_env()
            except docker.errors.DockerException:
                message.warning(
                    "Could not get response from docker. Is your docker-daemon running?"
                )
                sys.exit(0)
        return Docker._client

    @property
    def image(self):
        if not self._image:
            try:
                self._image = cast_image(self.client.images.get(self.tag))
            except docker.errors.ImageNotFound:
                message.info2(
                    f"Creating a new docker image for {Path(self.dockerfile).parent.name}"
                )
                self._image = build_image(
                    self.client, self.tag, str(Path(self.dockerfile).parent)
                )
            else:
                pass
        return self._image

    def __enter__(self):
        message.info(f"Starting container")
        self._container = cast_container(
            self.client.containers.run(
                self.image,
                auto_remove=True,
                detach=True,
                stdin_open=True,
                volumes=self.volume,
                name=self.name,
                command="/bin/sh",
                user=DPP_DOCKER_USER,
                working_dir=self.working_dir,
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
