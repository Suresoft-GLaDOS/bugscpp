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
DPP_CXBUILD_HOME: str = DPP_DOCKER_HOME + "/.cxbuild"
DPP_CXBUILD_URL: str = "https://github.com/Suresoft-GLaDOS/cxbuild/releases/download/dpp/Release-cxbuild-Ubuntu-18.04.tar.gz"
DPP_COMPILATION_DB_TOOL: str = DPP_CXBUILD_HOME + "/bin/cxbuild capture"
DPP_CMAKE_COMPILATION_DB_TOOL: str = DPP_CXBUILD_HOME + "/bin/cxbuild capture"
DPP_BUILD_PRE_STEPS: List[Dict[str, any]] = [
    {
        "type": "script",
        "lines": [
            "bash -c \"if [ ! -d " + DPP_CXBUILD_HOME + " ]; then mkdir " + DPP_CXBUILD_HOME + "; fi\"",
            "bash -c \"wget -O " + DPP_CXBUILD_HOME + "/cxbuild.tar.gz " + DPP_CXBUILD_URL + "\"",
            "bash -c \"tar zxvf " + DPP_CXBUILD_HOME + "/cxbuild.tar.gz -C " + DPP_CXBUILD_HOME + "\"",
        ]
    }
]

# Directory at which d++.py is placed
DPP_HOME: str = os.path.realpath(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")
)
