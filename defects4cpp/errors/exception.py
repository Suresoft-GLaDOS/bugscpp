import argparse
from pathlib import Path
from typing import Dict


class DppTaxonomyInitError(Exception):
    def __init__(self, key: str, data_name: str):
        super().__init__(
            f"Cannot initialize Taxonomy. {key} does not exist in {data_name}."
            f" Please check meta.json of Taxonomy"
        )
        self.key: str = key
        self.data_name = data_name


class DppTaxonomyNotFoundError(Exception):
    def __init__(self, taxonomy_name: str):
        super().__init__(f"taxonomy '{taxonomy_name}' does not exist")
        self.taxonomy_name: str = taxonomy_name


class DppTaxonomyNotProjectDirectory(Exception):
    def __init__(self, path: Path):
        super().__init__(f"directory '{str(path)}' is not a defect taxonomy project")
        self.path: Path = path


class DppDefectIndexError(Exception):
    def __init__(self, index: int):
        super().__init__(f"invalid index '{index}' of defects")
        self.index: int = index


class DppCaseExpressionInternalError(Exception):
    def __init__(self, namespace: argparse.Namespace):
        super().__init__(f"namespace={namespace}")
        self.namespace: argparse.Namespace = namespace


class DppInvalidCaseExpressionError(Exception):
    def __init__(self, index: int, name: str, cases: int, expr: str):
        super().__init__(
            f"Defect#{index} of {name} has {cases} test cases, but expression was: {expr}"
        )
        self.index: int = index
        self.name: str = name
        self.cases: int = cases
        self.expr: str = expr


class DppFileNotFoundError(FileNotFoundError):
    def __init__(self, path: str):
        super().__init__()
        self.path: str = path


class DppInvalidConfigError(Exception):
    def __init__(self):
        super().__init__()


class DppConfigCorruptedError(Exception):
    def __init__(self, data: Dict):
        super().__init__(f"config is corrupted: {data}")
        self.data = data


class DppConfigNotInitialized(Exception):
    def __init__(self):
        super().__init__("config is used before initialized")


class DppPatchError(Exception):
    def __init__(self, defect):
        super().__init__(f"could not get lua_path in {defect.split_patch}")
        self.defect = defect
