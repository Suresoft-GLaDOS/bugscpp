from pathlib import Path
from typing import Dict

from errors.common.exception import DppError


class DppArgparseError(DppError):
    pass


class DppAdditionalGcovOptionsWithoutCoverage(DppArgparseError):
    def __init__(self):
        super().__init__(
            f"'--additional-gcov-options' should be used with '--coverage' option"
        )


class DppArgparseTaxonomyNotFoundError(DppArgparseError):
    def __init__(self, taxonomy_name: str):
        super().__init__(f"taxonomy '{taxonomy_name}' does not exist")
        self.taxonomy_name: str = taxonomy_name


class DppArgparseNotProjectDirectory(DppArgparseError):
    def __init__(self, path: Path):
        super().__init__(f"directory '{str(path)}' is not a defect taxonomy project")
        self.path: Path = path


class DppArgparseDefectIndexError(DppArgparseError):
    def __init__(self, index: int):
        super().__init__(f"invalid index '{index}' of defects")
        self.index: int = index


class DppArgparseFileNotFoundError(DppArgparseError, FileNotFoundError):
    def __init__(self, path: str):
        super().__init__()
        self.path: str = path


class DppArgparseInvalidEnvironment(DppArgparseError):
    def __init__(self, value: str):
        super().__init__(
            f"invalid environment variable format '{value}' (should be KEY=VALUE)"
        )
        self.value: str = value


class DppArgparseInvalidConfigError(DppArgparseError):
    def __init__(self):
        super().__init__()


class DppArgparseConfigCorruptedError(DppArgparseError):
    def __init__(self, data: Dict):
        super().__init__(f"config is corrupted: {data}")
        self.data = data


class DppArgparseInvalidCaseExpressionError(DppArgparseError):
    def __init__(self, index: int, name: str, cases: int, expr: str):
        super().__init__(
            f"Defect#{index} of {name} has {cases} test cases, but expression was: {expr}"
        )
        self.index: int = index
        self.name: str = name
        self.cases: int = cases
        self.expr: str = expr
