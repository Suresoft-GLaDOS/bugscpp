"""
Base exception class for defects4cpp.

All user-defined exceptions should inherit from this class.
"""
from os import stat
from stat import filemode


class DppError(Exception):
    @staticmethod
    def print_path(path: str) -> str:
        """
        Path with its file stat.

        Parameters
        ----------
        path : str
            Path to file

        Returns
        -------
        str
            Return string of path with its stat information.
        """
        try:
            return f"{filemode(stat(path).st_mode)} {path}"
        except FileNotFoundError:
            return f"(nonexistent) {path}"
