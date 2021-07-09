from collections.abc import MutableMapping
from dataclasses import dataclass
from os.path import dirname, exists, join
from pkgutil import iter_modules
from typing import Dict, List, Optional

import hjson


@dataclass
class Common:
    root: str
    exclude: List[str]
    checkout: List[str]
    build_generator: str
    build_command: List[str]
    build_cov_generator: str
    build_cov_command: List[str]
    test_generator: str
    test_command: List[str]
    test_cov_generator: str
    test_cov_command: List[str]
    clean: List[str]


@dataclass
class Defect:
    hash: str
    buggy_patch: str
    split_patch: str
    cases: int


@dataclass
class MetaInfo:
    url: str
    description: str
    vcs: str


class MetaData:
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
        return self._common

    @property
    def defects(self):
        if not self._defects:
            self._load()
        return self._defects

    def _load(self):
        with open(f"{self._path}/meta.hjson", "r", encoding="utf-8") as fp:
            meta = hjson.load(fp)
        self._load_info(meta)
        self._load_common(meta)
        self._load_defects(meta)

    def _load_info(self, meta: Dict):
        try:
            self._defects = [
                Defect(
                    defect["hash"],
                    f"{self._path}/patch/{defect['patch']:04}-buggy.patch",
                    f"{self._path}/patch/{defect['patch']:04}-split.patch",
                    defect["cases"],
                )
                for defect in meta["defects"]
            ]
        except KeyError:
            pass

    def _load_common(self, meta: Dict):
        try:
            self._common = Common(
                meta["common"]["root"],
                [dir for dir in meta["common"]["exclude"]],
                meta["common"]["checkout"],
                meta["common"]["builder"]["generator"],
                meta["common"]["builder"]["command"],
                meta["common"]["builder-cov"]["generator"],
                meta["common"]["builder-cov"]["command"],
                meta["common"]["tester"]["generator"],
                meta["common"]["tester"]["command"],
                meta["common"]["tester-cov"]["generator"],
                meta["common"]["tester-cov"]["command"],
                meta["common"]["clean"],
            )
        except KeyError:
            pass

    def _load_defects(self, meta: Dict):
        try:
            self._info = MetaInfo(
                meta["info"]["url"], meta["info"]["short-desc"], meta["info"]["vcs"]
            )
        except KeyError:
            pass


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

    def __getitem__(self, key: str):
        return self.store[self._keytransform(key)]

    def __setitem__(self, key: str, value: MetaData):
        # self.store[self._keytransform(key)] = value
        raise RuntimeError("set operator is not allowed")

    def __delitem__(self, key: str):
        # del self.store[self._keytransform(key)]
        raise RuntimeError("del operator is not allowed")

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

    def _keytransform(self, key: str):
        assert exists(
            join(self.base, key, "meta.hjson")
        ), f"Taxonomy '{key}' does not exist"
        return key


__all__ = ["Taxonomy", "MetaData", "MetaInfo", "Defect", "Common"]
