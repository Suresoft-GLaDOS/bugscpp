from dataclasses import dataclass
from os import getcwd
from pathlib import Path
from typing import Dict, Optional, cast

import docker
import docker.errors
import message
import taxonomy
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

    def __init__(self):
        self._name: str = ""
        self._index: int = 1
        self._buggy: bool = False
        self._workspace: str = ""

    @property
    def base(self):
        return Path(f"{self._workspace}/{self._name}")

    @property
    def host(self):
        return self.base / f"{'buggy' if self._buggy else 'fixed'}#{self._index}"

    @property
    def container(self):
        return Path("/home/workspace")

    def __repr__(self):
        return f"{self._name=} {self._index=}, {self._buggy=}, {self._workspace=}"


class Docker:
    client = docker.from_env()

    def __init__(self, dockerfile: str, worktree: Worktree):
        self.dockerfile = dockerfile
        # Assumes that the name of its parent directory is the same with that of the target.
        tag = Path(dockerfile).parent.name
        self.name: str = f"{tag}-dpp-generated-container"
        self.tag: str = f"{tag}/dppgen"
        self._image: Optional[Image] = None
        self._container: Optional[Container] = None
        self.volume: Dict[str, Dict] = {
            str(worktree.host): {"bind": str(worktree.container), "mode": "rw"}
        }
        self.working_dir: str = str(worktree.container)

    @property
    def image(self):
        # TODO: message
        if not self._image:
            try:
                self._image = cast_image(self.client.images.get(self.tag))
            except docker.errors.ImageNotFound:
                message.info(
                    f"Creating a new docker image for {Path(self.dockerfile).parent.name}"
                )
                self._image = build_image(
                    self.client, self.tag, str(Path(self.dockerfile).parent)
                )
            else:
                pass
        return self._image

    def __enter__(self):
        self._container = cast_container(
            self.client.containers.run(
                self.image,
                auto_remove=True,
                detach=True,
                stdin_open=True,
                volumes=self.volume,
                name=self.name,
                command="bash",
                working_dir=self.working_dir,
            )
        )
        return self

    def __exit__(self, type, value, traceback):
        self._container.stop()

    def send(self, command: str, stream=True) -> ExecResult:
        return self._container.exec_run(command, stream=stream)