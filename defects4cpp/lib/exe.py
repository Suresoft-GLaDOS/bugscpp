import shlex
import subprocess


def run_cmd(cmd: str):
    return subprocess.call(shlex.split(cmd))
