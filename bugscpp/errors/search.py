from typing import List

import processor
from errors import DppError


class DppSearchError(DppError):
    pass


class DppNoSuchTagError(DppSearchError):
    def __init__(self, tags: List[str]):
        super().__init__(
            f"There is no such tag: '{ ', '.join(tags) }'.\n"
            f"All possible tags are: '{ ', '.join(processor.search.all_tags) }'."
        )
