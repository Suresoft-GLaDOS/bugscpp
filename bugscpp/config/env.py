"""
Configuration file for controlling defects4cpp.

"""
import os
from typing import Dict, List

# Docker username (should be the same with Dockerfile)
DPP_DOCKER_USER: str = "defects4cpp"
# Docker workspace (should be the same with Dockerfile)
DPP_DOCKER_HOME: str = "/home/workspace"

# meta.json variables
DPP_PARALLEL_BUILD: str = "1"
DPP_COMPILATION_DB_TOOL: str = "bear"
DPP_CMAKE_COMPILATION_DB_TOOL: str = ""
DPP_ADDITIONAL_GCOV_OPTIONS: str = ""
DPP_BUILD_PRE_STEPS: List[Dict[str, any]] = []
DPP_BUILD_POST_STEPS: List[Dict[str, any]] = []

# Directory at which bugcpp.py is placed
DPP_HOME: str = os.path.realpath(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")
)
