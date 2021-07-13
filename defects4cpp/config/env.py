import os

"""
Directory which d++.py is placed
"""
DPP_DOCKER_USER: str = "defects4cpp"
DPP_DOCKER_HOME: str = "/home/workspace"

DPP_HOME: str = os.path.realpath(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")
)
