import os

# Docker username (should be the same with Dockerfile)
DPP_DOCKER_USER: str = "defects4cpp"
# Docker workspace (should be the same with Dockerfile)
DPP_DOCKER_HOME: str = "/home/workspace"

# meta.json variables
DPP_PARALLEL_BUILD: str = "1"

# Directory at which d++.py is placed
DPP_HOME: str = os.path.realpath(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")
)
