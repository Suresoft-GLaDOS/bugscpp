import os

# Docker username (should be the same with Dockerfile)
DPP_DOCKER_USER: str = "defects4cpp"
# Docker workspace (should be the same with Dockerfiel)
DPP_DOCKER_HOME: str = "/home/workspace"
# Makefile job flag
DPP_MAKE_JOB: str = "-j1"

# Directory at which d++.py is placed
DPP_HOME: str = os.path.realpath(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")
)
