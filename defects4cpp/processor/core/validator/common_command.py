import argparse

from config import config


class ValidateCompilationDBTool(argparse.Action):
    """
    Validator for compilation db tool argument.
    """

    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: str,
        option_string=None,
    ):
        config.DPP_COMPILATION_DB_TOOL = values
        config.DPP_CMAKE_COMPILATION_DB_TOOL = values
