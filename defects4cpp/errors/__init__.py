from errors.argparser import (DppAdditionalGcovOptionsWithoutCoverage, DppArgparseConfigCorruptedError,
                              DppArgparseDefectIndexError, DppArgparseError, DppArgparseFileNotFoundError,
                              DppArgparseInvalidCaseExpressionError, DppArgparseInvalidConfigError,
                              DppArgparseInvalidEnvironment, DppArgparseNotProjectDirectory,
                              DppArgparseTaxonomyNotFoundError)
from errors.checkout import (DppGitApplyPatchError, DppGitCheckoutError, DppGitCheckoutInvalidRepositoryError,
                             DppGitCloneError, DppGitError, DppGitPatchNotAppliedError, DppGitSubmoduleInitError,
                             DppGitWorktreeError)
from errors.common.exception import DppError
from errors.docker import DppDockerError, DppDockerNoClientError
from errors.internal import DppCaseExpressionInternalError, DppCommandListInternalError, DppInternalError
from errors.search import DppNoSuchTagError, DppSearchError

__all__ = [
    "DppError",
    "DppArgparseError",
    "DppArgparseNotProjectDirectory",
    "DppArgparseInvalidEnvironment",
    "DppArgparseDefectIndexError",
    "DppArgparseTaxonomyNotFoundError",
    "DppArgparseInvalidConfigError",
    "DppArgparseConfigCorruptedError",
    "DppArgparseFileNotFoundError",
    "DppArgparseInvalidEnvironment",
    "DppArgparseInvalidCaseExpressionError",
    "DppGitError",
    "DppGitCheckoutError",
    "DppGitCheckoutInvalidRepositoryError",
    "DppGitApplyPatchError",
    "DppGitWorktreeError",
    "DppGitCloneError",
    "DppGitSubmoduleInitError",
    "DppGitPatchNotAppliedError",
    "DppInternalError",
    "DppCaseExpressionInternalError",
    "DppCommandListInternalError",
    "DppDockerError",
    "DppDockerNoClientError",
    "DppAdditionalGcovOptionsWithoutCoverage",
    "DppSearchError",
    "DppNoSuchTagError",
]
