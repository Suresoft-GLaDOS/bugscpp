"""
Manage commands associated with docker SDK module.

Do not use docker SDK directly, instead use Docker class.
"""
import sys
from pathlib import Path
from textwrap import dedent
from typing import Dict, Optional, cast

import docker
import docker.errors
from config import config
from docker import DockerClient
from docker.models.containers import Container, ExecResult
from docker.models.images import Image
from errors import DppError
from errors.docker import (
    DppDockerBuildClientError,
    DppDockerBuildError,
    DppDockerBuildServerError,
    DppDockerNoClientError,
)
from message import message
from processor.core.data import Worktree


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


def _try_build_image(client, tag, path) -> Image:
    try:
        return client.images.build(rm=True, tag=tag, path=path)[0]
    except docker.errors.BuildError as e:
        raise DppDockerBuildError(e.msg)
    except docker.errors.APIError as e:
        if e.is_client_error():
            raise DppDockerBuildClientError(e.explanation)
        else:
            raise DppDockerBuildServerError(e.explanation)


def _build_image(client, tag, path) -> Image:
    """
    Helper function to get a correct type
    """
    try:
        return _try_build_image(client, tag, path)
    except DppError as e:
        message.stdout_progress_error(e)
        sys.exit(1)


class _Client:
    def __get__(self, instance, owner) -> DockerClient:
        if getattr(owner, "_client", None) is None:
            try:
                setattr(owner, "_client", docker.from_env())
            except docker.errors.DockerException:
                message.error(__name__, "no response from docker-daemon")
                raise DppDockerNoClientError()
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

    def __init__(
        self,
        dockerfile: str,
        worktree: Worktree,
        environ: Optional[Dict[str, str]] = None,
        rebuild_image=False,
    ):
        self._dockerfile = dockerfile
        # Assumes that the name of its parent directory is the same with that of the target.
        tag = Path(dockerfile).parent.name
        self._name: str = f"{tag}-dpp-generated-container"
        self._tag: str = f"{tag}/dppgen"
        self._volume: Dict[str, Dict] = {
            str(worktree.host): {"bind": str(worktree.container), "mode": "rw"}
        }
        self._working_dir: str = str(worktree.container)
        self._environ = environ
        self._rebuild_image = rebuild_image
        self._image: Optional[Image] = None
        self._container: Optional[Container] = None

    @property
    def image(self) -> Image:
        """Docker SDK Image."""
        if not self._image:
            try:
                if self._rebuild_image:
                    # It should raise ImageNotFound later and make image rebuilt.
                    self.client.images.remove(self._tag)
                    message.info(__name__, f"removing the previous image {self._tag}")

                self._image = _cast_image(self.client.images.get(self._tag))
                message.info(__name__, f"image found {self._tag}")
            except docker.errors.ImageNotFound:
                tag_name = str(Path(self._dockerfile).parent.name)
                message.info(
                    __name__, f"no image found. creating new one using {tag_name}"
                )
                message.stdout_progress(f"Creating a new docker image for {tag_name}")
                self._image = _build_image(
                    self.client, self._tag, str(Path(self._dockerfile).parent)
                )
        return self._image

    def __enter__(self):
        k = list(self._volume)[0]
        message.info(
            __name__,
            dedent(
                """container.__enter__ ({})
                - from {}
                - to {}
                - mode {}""".format(
                    self._name,
                    DppError.print_path(k),
                    self._volume[k]["bind"],
                    self._volume[k]["mode"],
                )
            ),
        )
        message.stdout_progress_detail("Starting container")
        self._container = _cast_container(
            self.client.containers.run(
                self.image,
                auto_remove=True,
                command="/bin/sh",
                detach=True,
                environment=self._environ,
                name=self._name,
                stdin_open=True,
                user=config.DPP_DOCKER_USER,
                volumes=self._volume,
                working_dir=self._working_dir,
            )
        )
        return self

    def __exit__(self, type, value, traceback):
        message.info(__name__, f"container.__exit__ ({self._name})")
        message.stdout_progress_detail("Closing container")
        self._container.stop()

    def send(self, command: str, stream=True) -> ExecResult:
        """
        Send a single line command to the running container.
        """
        return self._container.exec_run(command, stream=stream)
