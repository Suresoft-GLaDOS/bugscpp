"""
Manage commands associated with shell.

Not fully implemented yet.
"""
import shlex
from shutil import which
from subprocess import PIPE, Popen, SubprocessError
from typing import Optional


class Shell:
    """
    Run commands with subprocess.
    It is highly recommend to use this via `with` statement.
    """

    def __init__(self):
        self.subprocess: Optional[Popen] = None
        self.shell = "bash" if which("bash") else "cmd"

    def __enter__(self):
        try:
            self.subprocess = Popen(
                self.shell, universal_newlines=True, stdin=PIPE, bufsize=1
            )
        except SubprocessError:
            # TODO: exception handling required
            return None
        return self

    def __exit__(self, type, value, traceback):
        self.subprocess.communicate(shlex.join(["exit"]))

    def send(self, commands):
        for command in commands:
            self.subprocess.stdin.write(f"{command}\n")
