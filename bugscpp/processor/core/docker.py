"""
Manage commands associated with docker SDK module.

Do not use docker SDK directly, instead use Docker class.
"""
import os
import sys
from pathlib import Path
from textwrap import dedent
from typing import Dict, Optional, cast

import docker.errors
from config import config
from docker import DockerClient
from docker.models.containers import Container, ExecResult
from docker.models.images import Image
from errors import DppError
from errors.docker import (DppDockerBuildClientError, DppDockerBuildError, DppDockerBuildServerError,
                           DppDockerNoClientError)
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


def _try_build_image(client, tag, path, verbose) -> Image:
    try:
        image, stream = client.images.build(rm=True, tag=tag, path=path, pull=True)
        if verbose:
            for chunk in stream:
                if "stream" in chunk:
                    for line in chunk["stream"].splitlines():
                        print(line)
        return image
    except docker.errors.BuildError as e:
        raise DppDockerBuildError(e.msg)
    except docker.errors.APIError as e:
        if e.is_client_error():
            raise DppDockerBuildClientError(e.explanation)
        else:
            raise DppDockerBuildServerError(e.explanation)


def _build_image(client, tag, path, verbose) -> Image:
    """
    Helper function to get a correct type
    """
    try:
        return _try_build_image(client, tag, path, verbose)
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
    It is recommended to use this via `with` statement.

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
        user=None,
        uid_of_user: Optional[str] = None,
        verbose=True,
    ):
        self._dockerfile = dockerfile
        # Assume that the parent directory has the same name as the target.
        tag = Path(dockerfile).parent.name
        self._container_name: str = f"{tag}-dpp"
        self._tag = f"hschoe/defects4cpp-ubuntu:{tag}"
        self._volume: Dict[str, Dict] = {
            str(worktree.host.resolve()): {
                "bind": str(worktree.container),
                "mode": "rw",
            }
        }
        self._working_dir: str = str(worktree.container)
        self._environ = environ
        self._rebuild_image = rebuild_image
        self._image: Optional[Image] = None
        self._container: Optional[Container] = None
        self._user = user
        self._uid_of_dpp_docker_user = uid_of_user
        self._verbose = verbose

    @property
    def image(self) -> Image:
        """Docker SDK Image."""
        if not self._image:
            message.stdout_progress_detail(f"  Image: {self._tag}")
            try:
                # SET DEFECTS4CPP_TEST_TAXONOMY to 1 for taxonomy testing
                if os.environ.get("DEFECTS4CPP_TEST_TAXONOMY", "0") not in ["YES", "1"]:
                    self.client.images.pull(self._tag)
                self._image = _cast_image(self.client.images.get(self._tag))
            except docker.errors.ImageNotFound:
                message.info(
                    f"ImageNotFound {self.client}, {self._tag}, {str(Path(self._dockerfile).parent)}"
                )
                self._image = _build_image(
                    self.client,
                    self._tag,
                    str(Path(self._dockerfile).parent),
                    self._verbose,
                )
            except docker.errors.APIError as api_error:
                message.stdout_error(
                    f"    An API Error occured.{os.linesep}"
                    f"    Find detailed message at {message.path}."
                )
                message.error(__name__, f"APIError {api_error}")
                self._image = _build_image(
                    self.client,
                    self._tag,
                    str(Path(self._dockerfile).parent),
                    self._verbose,
                )

            if self._uid_of_dpp_docker_user is not None:
                # set uid of user(defects4cpp) to self._uid_of_dpp_docker_user after checking if uid need to be changed
                _container = _cast_container(
                    self.client.containers.run(
                        self._image,
                        detach=True,
                        stdin_open=True,
                        environment=self._environ,
                        name=self._container_name,
                    )
                )
                _, output = _container.exec_run(f"id -u {config.DPP_DOCKER_USER}")
                uid = str(output, "utf-8").strip("\n")
                if self._uid_of_dpp_docker_user != uid:
                    message.stdout_progress_detail(
                        f"  Setting uid of {config.DPP_DOCKER_USER} "
                        f"from {uid} "
                        f"to {self._uid_of_dpp_docker_user}."
                    )
                    _, output = _container.exec_run(
                        f"usermod -u {self._uid_of_dpp_docker_user} {config.DPP_DOCKER_USER}"
                    )
                repository, tag = tuple(self._tag.split(":"))
                self._image = _cast_image(
                    _container.commit(repository=repository, tag=tag)
                )
                _container.stop()
                _container.remove()
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
                    self._container_name,
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
                name=self._container_name,
                stdin_open=True,
                user=config.DPP_DOCKER_USER if not self._user else self._user,
                volumes=self._volume,
                working_dir=self._working_dir,
            )
        )
        return self

    def __exit__(self, type, value, traceback):
        message.info(__name__, f"container.__exit__ ({self._container_name})")
        message.stdout_progress_detail("Closing container")
        self._container.stop()

    def send(self, command: str, stream=True, **kwargs) -> ExecResult:
        """
        Send a single line command to the running container.
        """
        return self._container.exec_run(command, stream=stream, **kwargs)
