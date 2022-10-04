import os
from pathlib import Path

import pytest
import taxonomy
from processor.core.argparser import create_common_vcs_parser
from processor.core.docker import Docker, Worktree


def create_dummy_worktree(path: Path) -> Worktree:
    parser = create_common_vcs_parser()
    args = parser.parse_args(f"yara 1 --target {str(path)}".split())
    return args.worktree


@pytest.mark.slow
def test_docker_image(tmp_path):
    t = taxonomy.Taxonomy()
    metadata = t["yara"]
    worktree = create_dummy_worktree(tmp_path)

    docker = Docker(metadata.dockerfile, worktree)
    assert docker.image is not None


@pytest.mark.slow
def test_docker_container(tmp_path):
    t = taxonomy.Taxonomy()
    metadata = t["yara"]
    worktree = create_dummy_worktree(tmp_path)

    with Docker(metadata.dockerfile, worktree) as docker:
        assert docker.send("echo Hello, world!", stream=False).exit_code == 0


@pytest.mark.slow
def test_docker_mount_directory(tmpdir):
    t = taxonomy.Taxonomy()
    metadata = t["yara"]
    worktree = create_dummy_worktree(tmpdir)
    worktree.host.mkdir(parents=True)
    # FIXME: Due to Github Action bug, it creates a directory owned by root even if user option is specified.
    worktree.host.chmod(0o777)

    dummy = "foo.txt"
    dummy_path = os.path.join(worktree.host, dummy)

    with Docker(metadata.dockerfile, worktree) as docker:
        assert docker.send(f"touch {dummy}", stream=False).exit_code == 0

    assert os.path.exists(dummy_path)

    with Docker(metadata.dockerfile, worktree) as docker:
        assert docker.send(f"rm {dummy}", stream=False).exit_code == 0

    assert not os.path.exists(dummy_path)
