from textwrap import dedent
from typing import TYPE_CHECKING, List, Tuple, Union

import git
from errors.common.exception import DppError

if TYPE_CHECKING:
    from taxonomy.taxonomy import Defect, MetaData


class DppGitError(DppError):
    pass


class DppGitCloneError(DppGitError):
    def __init__(
        self,
        metadata: "MetaData",
        path: str,
        command: Union[List[str], Tuple[str, ...], str],
        status: Union[str, int, None, Exception],
        stdout: Union[bytes, str, None],
    ):
        self.metadata = metadata
        self.path = path
        self.command = command
        self.status = status
        self.stdout = stdout
        super().__init__(
            dedent(
                """git-clone failed.
                Command: {}
                Status: {}
                Path: {}
                Metadata: {}
                """.format(
                    " ".join(self.command),
                    self.status,
                    self.print_path(self.path),
                    self.metadata.name,
                )
            )
        )


class DppGitWorktreeError(DppGitError):
    def __init__(self, repo: git.Repo, path: str, defect: "Defect"):
        self.repo = repo
        self.path = path
        self.defect = defect
        super().__init__(
            dedent(
                """git-worktree failed.
                Path: {}
                Defect: {}
                """.format(
                    self.print_path(self.path), self.defect
                )
            )
        )


class DppGitCheckoutInvalidRepositoryError(DppGitError):
    def __init__(self, repo: git.Repo, path: str, defect: "Defect"):
        self.repo = repo
        self.path = path
        self.defect = defect
        super().__init__(
            dedent(
                """git-checkout failed (not a git repository).
                Path: {}
                Defect: {}
                """.format(
                    self.print_path(self.path), self.defect
                )
            )
        )


class DppGitCheckoutError(DppGitError):
    def __init__(self, repo: git.Repo, path: str, defect: "Defect"):
        self.repo = repo
        self.path = path
        self.defect = defect
        super().__init__(
            dedent(
                """git-checkout failed.
                Path: {}
                Defect: {}
                """.format(
                    self.print_path(self.path), self.defect
                )
            )
        )


class DppGitSubmoduleInitError(DppGitError):
    def __init__(
        self,
        repo: git.Repo,
        command: Union[List[str], Tuple[str, ...], str],
        status: Union[str, int, None, Exception],
        stdout: Union[bytes, str, None],
    ):
        self.repo = repo
        self.command = command
        self.status = status
        self.stdout = stdout
        super().__init__(
            dedent(
                """git-submodule failed.
                Command: {}
                Status: {}
                Output: {}
                """.format(
                    " ".join(self.command), self.status, self.stdout
                )
            )
        )


class DppGitApplyPatchError(DppGitError):
    def __init__(
        self,
        repo: git.Repo,
        patch: str,
        command: Union[List[str], Tuple[str, ...], str],
        status: Union[str, int, None, Exception],
        stdout: Union[bytes, str, None],
    ):
        self.repo = repo
        self.patch = patch
        self.command = command
        self.status = status
        self.stdout = stdout
        super().__init__(
            dedent(
                """git-am failed.
                Patch: {}
                Command: {}
                Status: {}
                Output: {}
                """.format(
                    self.print_path(self.patch),
                    " ".join(self.command),
                    self.status,
                    self.stdout,
                )
            )
        )


class DppGitPatchNotAppliedError(DppGitError):
    def __init__(self, repo: git.Repo, patch: str):
        self.repo = repo
        self.patch = patch
        super().__init__(
            dedent(
                """git-am failed.
                Patch: {}
                """.format(
                    self.print_path(self.patch)
                )
            )
        )
