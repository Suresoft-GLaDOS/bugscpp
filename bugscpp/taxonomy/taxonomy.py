import enum
import json
from collections.abc import Mapping
from dataclasses import dataclass, fields
from os.path import dirname, exists, join
from pkgutil import iter_modules
from typing import Any, Callable, Dict, Iterator, List, Optional

from config import config
from errors.internal import DppMetaDataInitKeyError, DppMetaDataInitTypeError, DppTaxonomyInitInternalError


class CommandType(enum.IntEnum):
    Docker = 1
    Script = 2


@dataclass(frozen=True)
class Command:
    type: CommandType
    lines: List[str]


@dataclass(frozen=True)
class ExtraTest(Command):
    is_pass: bool


class TestType(enum.IntEnum):
    Automake = 1
    Ctest = 2
    Googletest = 3
    Kyua = 4


@dataclass(frozen=True)
class Common:
    build_command: List[Command]
    build_coverage_command: List[Command]
    test_type: TestType
    test_command: List[Command]
    test_coverage_command: List[Command]
    gcov: "Gcov"


@dataclass(frozen=True)
class Gcov:
    exclude: List[str]
    command: List[Command]


@dataclass(frozen=True)
class Defect:
    hash: str
    buggy_patch: str
    fixed_patch: str
    common_patch: str
    split_patch: str
    id: int
    num_cases: int
    case: List[int]
    tags: List[str]
    description: str
    extra_tests: List[ExtraTest]


@dataclass(frozen=True)
class MetaInfo:
    url: str
    description: str
    vcs: str


def create_command(value: List[Dict[str, Any]]) -> List[Command]:
    return [Command(CommandType[v["type"].capitalize()], v["lines"]) for v in value]


def create_gcov(value: Dict[str, Any]) -> Gcov:
    return Gcov(
        [d for d in value["exclude"]],
        create_command(value["commands"]),
    )


def create_common(value: Dict[str, Any]) -> Common:
    return Common(
        create_command(value["build"]["commands"]),
        create_command(value["build-coverage"]["commands"]),
        TestType[value["test-type"].capitalize()],
        create_command(value["test"]["commands"]),
        create_command(value["test-coverage"]["commands"]),
        create_gcov(value["gcov"]),
    )


def create_info(value: Dict[str, Any]) -> MetaInfo:
    return MetaInfo(value["url"], value["short-desc"], value["vcs"])


class _MetaDataVariables(Mapping):
    def __init__(self, *args, **kwargs):
        self._store = dict(*args, **kwargs)

    def __getitem__(self, k: str) -> str:
        # Remove cmake export macro when DPP_CMAKE_COMPILATION_DB_TOOL is set.
        if k == "@DPP_CMAKE_GEN_COMPILATION_DB@" and getattr(
            config, "DPP_CMAKE_COMPILATION_DB_TOOL"
        ):
            return ""

        v: Optional[str] = self._store[k]
        if v is None:
            v = getattr(config, k.strip("@"))
        return v

    def __len__(self) -> int:
        return len(self._store)

    def __iter__(self) -> Iterator:
        return iter(self._store)

    def __eq__(self, other):
        return self._store == other


def _do_replace(variables: Dict, string: str) -> str:
    return " ".join([variables.get(w, w) for w in string.split()])


def _do_strip(variables: Dict, string: str) -> str:
    return " ".join([w for w in string.split() if w not in variables])


class MetaData:
    _variables = _MetaDataVariables(
        {
            "@DPP_PARALLEL_BUILD@": None,
        }
    )
    _common_variables = _MetaDataVariables(
        {
            "@DPP_CMAKE_GEN_COMPILATION_DB@": "-DCMAKE_EXPORT_COMPILE_COMMANDS=1",
            "@DPP_COMPILATION_DB_TOOL@": None,
            "@DPP_CMAKE_COMPILATION_DB_TOOL@": None,
            "@DPP_ADDITIONAL_GCOV_OPTIONS@": None,
        }
    )

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
    def common_gcov_replaced(self):
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
                    check_path(f"{self._path}/patch/{index:04}-fixed.patch"),
                    check_path(f"{self._path}/patch/{index:04}-common.patch"),
                    check_path(f"{self._path}/patch/{index:04}-split.patch"),
                    defect["id"],
                    defect["num_cases"],
                    defect["case"],
                    defect["tags"],
                    defect["description"],
                    [
                        [ExtraTest(e["type"], e["lines"], e["is_pass"]) for e in et]
                        for et in defect["extra_tests"]
                    ]
                    if "extra_tests" in defect
                    else [],
                )
                for index, defect in enumerate(meta["defects"], start=1)
            ]
        except KeyError as e:
            raise DppTaxonomyInitInternalError(e.args[0], MetaInfo.__name__)

    @staticmethod
    def _preprocess_common(common: Common, replace: bool) -> Common:
        data: Dict = {
            "test_type": common.test_type,
            "gcov": common.gcov,
        }

        func: Callable[[Dict, str], str] = _do_replace if replace else _do_strip
        command_fields = [f for f in fields(common) if f.type == List[Command]]
        for command_field in command_fields:
            objs: List[Command] = getattr(common, command_field.name)
            data[command_field.name] = [
                Command(
                    obj.type,
                    [func(MetaData._common_variables, line) for line in obj.lines],
                )
                for obj in objs
            ]

        MetaData._preprocess_build_command(func, data)
        MetaData._preprocess_gcov_command(func, data)
        return Common(**data)

    @staticmethod
    def _preprocess_build_command(
        func: Callable[[Dict, str], str], data: Dict[str, Any]
    ):
        def create_commands(steps: List[Dict[str, Any]]) -> List[Command]:
            commands: List[Command] = []
            for step in steps:
                try:
                    assert step["type"].capitalize() in valid_keys
                    commands.append(
                        Command(
                            step["type"].capitalize(),
                            [
                                func(MetaData._common_variables, line)
                                for line in step["lines"]
                            ],
                        )
                    )
                except KeyError:
                    raise DppMetaDataInitKeyError(step)
                except AssertionError:
                    raise DppMetaDataInitTypeError(step)
            return commands

        valid_keys = tuple(e.name for e in CommandType)
        build_fields = ("build_command", "build_coverage_command")

        for build_field in build_fields:
            pre_steps = create_commands(config.DPP_BUILD_PRE_STEPS)
            post_steps = create_commands(config.DPP_BUILD_POST_STEPS)
            data[build_field] = pre_steps + data[build_field] + post_steps

    # TODO: extend below functions for test and gcov command.
    @staticmethod
    def _preprocess_test_command(
        func: Callable[[Dict, str], str], data: Dict[str, Any]
    ):
        pass

    @staticmethod
    def _preprocess_gcov_command(
        func: Callable[[Dict, str], str], data: Dict[str, Any]
    ):
        for command_index, command in enumerate(data["gcov"].command):
            for line_index, line in enumerate(command.lines):
                command.lines[line_index] = func(MetaData._common_variables, line)
            data["gcov"].command[command_index] = command


class _LazyTaxonomy:
    def __set_name__(self, owner, name):
        self.name = f"_{name}"

    def __get__(self, instance, owner):
        try:
            return getattr(owner, self.name)
        except AttributeError:
            setattr(owner, self.name, self._load_taxonomy(instance.base))
        return getattr(owner, self.name)

    @staticmethod
    def _load_taxonomy(base: str) -> Dict[str, MetaData]:
        d = dict(
            [
                (name, MetaData(name, f"{join(base, name)}"))
                for _, name, is_pkg in iter_modules([dirname(__file__)])
                if is_pkg
            ]
        )
        return d


class Taxonomy(Mapping):
    _lazy_taxonomy = _LazyTaxonomy()

    def __init__(self):
        self.base: str = dirname(__file__)

    @property
    def _store(self) -> Dict[str, MetaData]:
        return self._lazy_taxonomy

    def __getitem__(self, key: str) -> MetaData:
        return self._store[self._keytransform(key)]

    def __iter__(self) -> Iterator:
        return iter(self._store)

    def __len__(self) -> int:
        return len(self._store)

    def _keytransform(self, key: str):
        assert exists(
            join(self.base, key, "meta.json")
        ), f"Taxonomy '{key}' does not exist"
        return key
