import enum
import json
from collections.abc import MutableMapping
from dataclasses import dataclass, fields
from os.path import dirname, exists, join
from pkgutil import iter_modules
from typing import Any, Callable, Dict, List, Optional

import config
from errors.internal import DppTaxonomyInitInternalError


class CommandType(enum.IntEnum):
    Docker = 1
    Script = 2


@dataclass(frozen=True)
class Command:
    type: CommandType
    lines: List[str]


class TestType(enum.IntEnum):
    Automake = 1
    Ctest = 2
    Googletest = 3
    Kyua = 4


@dataclass(frozen=True)
class Common:
    build_command: Command
    build_coverage_command: Command
    test_type: TestType
    test_command: Command
    test_coverage_command: Command
    gcov: "Gcov"


@dataclass(frozen=True)
class Gcov:
    exclude: List[str]
    command: Command


@dataclass(frozen=True)
class Defect:
    hash: str
    buggy_patch: str
    fix_patch: str
    split_patch: str
    num_cases: int
    case: List[int]
    description: str


@dataclass(frozen=True)
class MetaInfo:
    url: str
    description: str
    vcs: str


def create_command(value: Dict[str, Any]) -> Command:
    return Command(CommandType[value["type"].capitalize()], value["lines"])


def create_gcov(value: Dict[str, Any]) -> Gcov:
    return Gcov(
        [d for d in value["exclude"]],
        create_command(value["command"]),
    )


def create_common(value: Dict[str, Any]) -> Common:
    return Common(
        create_command(value["build"]["command"]),
        create_command(value["build-coverage"]["command"]),
        TestType[value["test-type"].capitalize()],
        create_command(value["test"]["command"]),
        create_command(value["test-coverage"]["command"]),
        create_gcov(value["gcov"]),
    )


def create_info(value: Dict[str, Any]) -> MetaInfo:
    return MetaInfo(value["url"], value["short-desc"], value["vcs"])


class MetaData:
    _variables: Dict[str, str] = {
        "@DPP_PARALLEL_BUILD@": config.DPP_PARALLEL_BUILD,
    }
    _common_variables: Dict[str, str] = {
        "@DPP_CMAKE_GEN_COMPILATION_DB@": "-DCMAKE_EXPORT_COMPILE_COMMANDS",
        "@DPP_GEN_COMPILATION_DB_TOOL@": config.DPP_COMPILATION_DB_TOOL,
    }

    def __init__(self, name: str, path: str):
        self.name = name
        self._path: str = path
        self._info: Optional[MetaInfo] = None
        self._common: Optional[Common] = None
        self._defects: List[Defect] = []

    @property
    def dockerfile(self) -> str:
        return f"{self._path}/Dockerfile"

    @property
    def info(self):
        if not self._info:
            self._load()
        return self._info

    @property
    def common(self):
        if not self._common:
            self._load()
        return self._preprocess_common(self._common, False)

    @property
    def common_capture(self):
        if not self._common:
            self._load()
        return self._preprocess_common(self._common, True)

    @property
    def defects(self):
        if not self._defects:
            self._load()
        return self._defects

    def _load(self):
        with open(f"{self._path}/meta.json", "r", encoding="utf-8") as fp:
            contents: str = fp.read()
            for key, value in self._variables.items():
                contents = contents.replace(key, value)
            meta = json.loads(contents)
        self._load_info(meta)
        self._load_common(meta)
        self._load_defects(meta)

    def _load_info(self, meta: Dict):
        try:
            self._info = create_info(meta["info"])
        except KeyError as e:
            raise DppTaxonomyInitInternalError(e.args[0], Defect.__name__)

    def _load_common(self, meta: Dict):
        try:
            self._common = create_common(meta["common"])
        except KeyError as e:
            raise DppTaxonomyInitInternalError(e.args[0], Common.__name__)

    def _load_defects(self, meta: Dict):
        def check_path(path: str) -> str:
            return path if exists(path) else ""

        try:
            self._defects = [
                Defect(
                    defect["hash"],
                    check_path(f"{self._path}/patch/{index:04}-buggy.patch"),
                    check_path(f"{self._path}/patch/{index:04}-fix.patch"),
                    check_path(f"{self._path}/patch/{index:04}-split.patch"),
                    defect["num_cases"],
                    defect["case"],
                    defect["description"],
                )
                for index, defect in enumerate(meta["defects"], start=1)
            ]
        except KeyError as e:
            raise DppTaxonomyInitInternalError(e.args[0], MetaInfo.__name__)

    @staticmethod
    def _preprocess_common(common: Common, replace: bool) -> Common:
        def do_replace(string: str) -> str:
            return " ".join(
                [MetaData._common_variables.get(w, w) for w in string.split()]
            )

        def do_strip(string: str) -> str:
            return " ".join(
                [
                    w
                    for w in string.split()
                    if w not in MetaData._common_variables.keys()
                ]
            )

        data: Dict = {
            "test_type": common.test_type,
            "gcov": common.gcov,
        }

        func: Callable[[str], str] = do_replace if replace else do_strip
        command_fields = [f for f in fields(common) if f.type == Command]
        for command_field in command_fields:
            obj = getattr(common, command_field.name)
            data[command_field.name] = Command(
                obj.type, [func(line) for line in obj.lines]
            )

        return Common(**data)


class Taxonomy(MutableMapping):
    def __init__(self, *args, **kwargs):
        self.base: str = dirname(__file__)
        self.store: Dict[str, MetaData] = dict(
            [
                (name, MetaData(name, f"{join(self.base, name)}"))
                for _, name, _ in iter_modules([dirname(__file__)])
            ]
        )
        # self.update(dict(*args, **kwargs))

    def __getitem__(self, key: str) -> MetaData:
        return self.store[self._keytransform(key)]

    def __setitem__(self, key: str, value: MetaData) -> None:
        # self.store[self._keytransform(key)] = value
        raise RuntimeError("set operator is not allowed")

    def __delitem__(self, key: str) -> None:
        # del self.store[self._keytransform(key)]
        raise RuntimeError("del operator is not allowed")

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

    def _keytransform(self, key: str):
        assert exists(
            join(self.base, key, "meta.json")
        ), f"Taxonomy '{key}' does not exist"
        return key
