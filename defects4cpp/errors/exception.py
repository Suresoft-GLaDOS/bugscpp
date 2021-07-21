import argparse

import taxonomy


class DppTaxonomyInitError(Exception):
    def __init__(self, key: str, data_name: str):
        super().__init__(
            f"Cannot initialize Taxonomy. {key} does not exist in {data_name}."
            f" Please check meta.json of Taxonomy"
        )
        self.key: str = key
        self.data_name = data_name


class DppTaxonomyNotFoundError(Exception):
    def __init__(self, taxonomy: str):
        super().__init__(f"taxonomy '{taxonomy}' does not exist")
        self.taxonomy: str = taxonomy


class DppDefectIndexError(Exception):
    def __init__(self, index: int):
        super().__init__(f"invalid index '{index}' of defects")
        self.index: int = index


class DppCommandLineInternalError(Exception):
    def __init__(self, attr: str):
        super().__init__(f"project is not set, but {attr} is invoked first")
        self.attr: str = attr


class DppCaseExpressionInternalError(Exception):
    def __init__(self, namespace: argparse.Namespace):
        super().__init__(f"namespace={namespace}")
        self.namespace: argparse.Namespace = namespace


class DppInvalidCaseExpressionError(Exception):
    def __init__(self, index: int, name: str, cases: int, expr: str):
        super().__init__(
            f"Defect#{index} of {name} has {cases}, but expression was: {expr}"
        )
        self.index: int = index
        self.name: str = name
        self.cases: int = cases
        self.expr: str = expr


class DppFileNotFoundError(FileNotFoundError):
    def __init__(self, path: str):
        super().__init__()
        self.path: str = path


class DppPatchError(Exception):
    def __init__(self, defect: taxonomy.Defect):
        super().__init__(f"could not get lua_path in {defect.split_patch}")
        self.defect: taxonomy.Defect = defect
