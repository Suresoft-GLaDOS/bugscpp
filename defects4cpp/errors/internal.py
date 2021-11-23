import argparse
import json
from dataclasses import fields
from typing import Dict

from errors.common.exception import DppError


class DppInternalError(DppError):
    pass


class DppCaseExpressionInternalError(DppInternalError):
    def __init__(self, namespace: argparse.Namespace):
        super().__init__(f"namespace={namespace}")
        self.namespace: argparse.Namespace = namespace


class DppCommandListInternalError(DppInternalError):
    def __init__(self):
        super().__init__(f"{self.__class__} object does not support item assignment")


class DppTaxonomyInitInternalError(DppInternalError):
    def __init__(self, key: str, data_name: str):
        super().__init__(
            f"Cannot initialize Taxonomy. {key} does not exist in {data_name}."
            " Please check meta.json of Taxonomy"
        )
        self.key: str = key
        self.data_name = data_name


class DppMetaDataInitKeyError(DppInternalError):
    def __init__(self, value: Dict):
        # Put here to avoid cyclic imports.
        from taxonomy import Command

        super().__init__(
            "Cannot initialize Metadata.\n"
            f"{json.dumps(value, indent=2)} is ill-formed."
            " Please check your config.\n"
            f"Required keys are [{', '.join(f.name for f in fields(Command))}], "
            f"but got [{', '.join(k for k in value)}]."
        )
        self.value: Dict = value


class DppMetaDataInitTypeError(DppInternalError):
    def __init__(self, value: Dict):
        # Put here to avoid cyclic imports.
        from taxonomy import CommandType

        super().__init__(
            "Cannot initialize Metadata.\n"
            f"{json.dumps(value, indent=2)} is ill-formed."
            " Please check your config\n"
            f"Valid enum values are [{', '.join(e.name for e in CommandType)}], "
            f"but got '{value['type']}'."
        )
        self.value: Dict = value
