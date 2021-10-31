import argparse

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
