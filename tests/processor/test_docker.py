import os

import defects4cpp.taxonomy
from defects4cpp.processor.core.docker import Docker


def test_docker_image(tmp_path):
    t = defects4cpp.taxonomy.Taxonomy()
    metadata = t["libsndfile"]
    docker = Docker(metadata.dockerfile, tmp_path)
    assert docker.image is not None


def test_docker_container(tmp_path):
    t = defects4cpp.taxonomy.Taxonomy()
    metadata = t["libsndfile"]
    with Docker(metadata.dockerfile, tmp_path) as docker:
        assert docker.send("echo Hello, world!", stream=False).exit_code == 0


def test_docker_mount_directory(tmp_path):
    t = defects4cpp.taxonomy.Taxonomy()
    metadata = t["libsndfile"]
    dummy = "foo.txt"
    dummy_path = os.path.join(tmp_path, dummy)

    with Docker(metadata.dockerfile, tmp_path) as docker:
        assert docker.send(f"touch {dummy}", stream=False).exit_code == 0

    assert os.path.exists(dummy_path)

    with Docker(metadata.dockerfile, tmp_path) as docker:
        assert docker.send(f"rm {dummy}", stream=False).exit_code == 0

    assert not os.path.exists(dummy_path)
