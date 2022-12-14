import logging
import tempfile
from collections.abc import MutableMapping
from logging.handlers import RotatingFileHandler
from os.path import dirname
from pathlib import Path
from pkgutil import iter_modules
from textwrap import TextWrapper, dedent, fill, indent
from typing import Dict, Optional, Tuple

from colorama import Fore, init

init()


class _MessageWhiteList(logging.Filter):
    _modules: Optional[Tuple[str]] = None

    def filter(self, record):
        if not _MessageWhiteList._modules:
            pkgpath = dirname(dirname(__file__))
            modules = tuple(name for _, name, _ in iter_modules([pkgpath]))
            _MessageWhiteList._modules = (
                tuple(
                    "__main__",
                )
                + modules
            )

        return record.name.startswith(_MessageWhiteList._modules)


class _MessageConfig(MutableMapping):
    def __init__(self, *args, **kwargs):
        self._store: Dict = dict(*args, **kwargs)

    def __getitem__(self, key: str):
        return self._store[self._keytransform(key)]

    def __setitem__(self, key: str, value):
        self._store[self._keytransform(key)] = value
        # (python 3.8) 'force' option should be preferred.
        logging.root.handlers = []
        logging.basicConfig(**self._store)

    def __delitem__(self, key: str):
        del self._store[self._keytransform(key)]

    def __iter__(self):
        return iter(self._store)

    def __len__(self):
        return len(self._store)

    def _keytransform(self, key: str):
        return key


class _Message:
    def __init__(self):
        temp = Path(tempfile.gettempdir()) / "defects4cpp.log"
        self._config = _MessageConfig(
            {
                "format": "%(levelname)s[%(name)s]: %(message)s",
                "level": logging.INFO,
                "handlers": [self._create_file_handler(temp)],
                # "force": True,  # (python 3.8) Some third party libraries might have touched it.
            }
        )
        logging.root.handlers = []
        logging.basicConfig(**self._config)
        self._wrapper = TextWrapper()

        # Disable information about where calls were made from.
        logging._srcfile = None
        # Disable threading information.
        logging.logThreads = 0
        # Disable process information.
        logging.logProcesses = 0

    @property
    def path(self) -> str:
        return logging.getLoggerClass().root.handlers[0].baseFilename

    @path.setter
    def path(self, path: Path):
        if path.is_dir():
            path /= "defects4cpp.log"
        self._config["handlers"] = [self._create_file_handler(path)]

    @staticmethod
    def _create_file_handler(path: Path) -> RotatingFileHandler:
        handler = RotatingFileHandler(path, maxBytes=100_000, backupCount=5)
        handler.addFilter(_MessageWhiteList())
        return handler

    @staticmethod
    def critical(module_name: str, msg: str):
        logging.getLogger(module_name).critical(msg)

    @staticmethod
    def error(module_name: str, msg: str):
        logging.getLogger(module_name).error(msg)

    @staticmethod
    def warning(module_name: str, msg: str):
        logging.getLogger(module_name).warning(msg)

    @staticmethod
    def debug(module_name: str, msg: str):
        logging.getLogger(module_name).debug(msg)

    @staticmethod
    def info(module_name: str, msg: str):
        logging.getLogger(module_name).info(msg)

    @staticmethod
    def stdout_title(msg: str):
        print(f"{Fore.BLUE}{msg}{Fore.RESET}")

    def stdout_bullet(self, msg: str):
        print(
            f"{Fore.GREEN}"
            f"{fill(dedent(msg), initial_indent='* ', subsequent_indent='  ', width=self._wrapper.width)}"
            f"{Fore.RESET}"
        )

    def stdout_paragraph(self, msg: str):
        print(
            f"{Fore.WHITE}"
            f"{indent(self._wrapper.fill(msg), prefix='  ', predicate=lambda line: True)}"
            f"{Fore.RESET}"
        )

    @staticmethod
    def stdout_progress(msg: str):
        print(f"{Fore.CYAN}{msg}{Fore.RESET}")

    @staticmethod
    def stdout_progress_detail(msg: str):
        print(f"  {Fore.GREEN}{msg}{Fore.RESET}")

    @staticmethod
    def stdout_progress_error(msg: str):
        print(f"{Fore.RED}{msg}{Fore.RESET}")

    @staticmethod
    def stdout_argparse_error(msg: str):
        print(f"{Fore.YELLOW}{msg}{Fore.RESET}")

    @staticmethod
    def stdout_search_error(msg: str):
        print(f"{Fore.YELLOW}{msg}{Fore.RESET}")

    @staticmethod
    def stdout_error(msg: str):
        print(f"{Fore.RED}{msg}{Fore.RESET}")

    @staticmethod
    def stdout_stream(msg: str):
        print(f"{Fore.LIGHTBLUE_EX}{msg}{Fore.RESET}", end="")


message = _Message()
