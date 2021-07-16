import os
from pathlib import Path

import defects4cpp.taxonomy
from defects4cpp.processor.core.argparser import create_taxonomy_parser
from defects4cpp.processor.core.docker import Docker, Worktree


def create_dummy_worktree(path: Path) -> Worktree:
    parser = create_taxonomy_parser()
    args = parser.parse_args(["--project", "yara", "--no", "1", "--target", str(path)])
    return args.worktree


def test_docker_image(tmp_path):
    t = defects4cpp.taxonomy.Taxonomy()
    metadata = t["yara"]
    worktree = create_dummy_worktree(tmp_path)

    docker = Docker(metadata.dockerfile, worktree)
    assert docker.image is not None


def test_docker_container(tmp_path):
    t = defects4cpp.taxonomy.Taxonomy()
    metadata = t["yara"]
    worktree = create_dummy_worktree(tmp_path)

    with Docker(metadata.dockerfile, worktree) as docker:
        assert docker.send("echo Hello, world!", stream=False).exit_code == 0


def test_docker_mount_directory(tmpdir):
    t = defects4cpp.taxonomy.Taxonomy()
    metadata = t["yara"]
    worktree = create_dummy_worktree(tmpdir)
    worktree.host.mkdir(parents=True)

    dummy = "foo.txt"
    dummy_path = os.path.join(worktree.host, dummy)

    with Docker(metadata.dockerfile, worktree) as docker:
        assert docker.send(f"touch {dummy}", stream=False).exit_code == 0

    assert os.path.exists(dummy_path)

    with Docker(metadata.dockerfile, worktree) as docker:
        assert docker.send(f"rm {dummy}", stream=False).exit_code == 0

    assert not os.path.exists(dummy_path)
