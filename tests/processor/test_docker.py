import os

import defects4cpp.taxonomy
from defects4cpp.processor.core.docker import Docker


def test_docker_image():
    t = defects4cpp.taxonomy.Taxonomy()
    metadata = t["libsndfile"]
    docker = Docker(metadata.dockerfile, "/home/haku/workspace/github/temp")
    assert docker.image is not None


def test_docker_container():
    t = defects4cpp.taxonomy.Taxonomy()
    metadata = t["libsndfile"]
    with Docker(metadata.dockerfile, "/home/haku/workspace/github/temp") as docker:
        assert docker.send("echo Hello, world!").exit_code == 0


def test_docker_mount_directory():
    t = defects4cpp.taxonomy.Taxonomy()
    metadata = t["libsndfile"]
    host_dir = "/home/haku/workspace/github/temp"
    dummy = "foo.txt"
    dummy_path = os.path.join(host_dir, dummy)

    with Docker(metadata.dockerfile, host_dir) as docker:
        assert docker.send(f"touch {dummy}").exit_code == 0

    assert os.path.exists(dummy_path)

    with Docker(metadata.dockerfile, host_dir) as docker:
        assert docker.send(f"rm {dummy}").exit_code == 0

    assert not os.path.exists(dummy_path)
