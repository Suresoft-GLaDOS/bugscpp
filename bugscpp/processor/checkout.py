"""
Checkout command.

Clone a repository into the given directory on the host machine.
"""
import os.path
import shutil
import sys
from pathlib import Path
from textwrap import dedent
from typing import Dict, List, Type

import git
import taxonomy
from errors import (DppGitApplyPatchError, DppGitCheckoutError, DppGitCheckoutInvalidRepositoryError, DppGitCloneError,
                    DppGitError, DppGitPatchNotAppliedError, DppGitSubmoduleInitError, DppGitWorktreeError)
from message import message
from processor.core.argparser import create_common_vcs_parser
from processor.core.command import Command
from processor.core.data import Project
from processor.core.docker import Docker


def _git_clone(path: Path, metadata: taxonomy.MetaData) -> git.Repo:
    """
    Initialize repository or clone a new one if it does not exist.
    """
    try:
        repo = git.Repo(str(path))
    except git.NoSuchPathError:
        if not path.parent.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
        message.info(__name__, f"cloning {metadata.name} into {str(path)}")
        try:
            repo = git.Repo.clone_from(
                metadata.info.url, str(path), multi_options=["-c core.autocrlf=false"]
            )
        except git.GitCommandError as e:
            raise DppGitCloneError(metadata, str(path), e.command, e.status, e.stdout)

    return repo


def _git_checkout(
    repo: git.Repo, checkout_dir: Path, defect: taxonomy.Defect
) -> git.Repo:
    """
    Checkout branch to the given commit.
    """
    if not checkout_dir.exists():
        try:
            # Pass '-f' in case worktree directory could be registered but removed.
            repo.git.worktree("add", "-f", str(checkout_dir.resolve()), defect.hash)
        except git.GitCommandError:
            raise DppGitWorktreeError(repo, str(checkout_dir.resolve()), defect)

        # git worktree list --porcelain will output
        # $ worktree path
        # $ ...
        porcelain_output = repo.git.worktree("list", "--porcelain").split("\n\n")
        dir_start_index = len("worktree ") + 1
        directory_names = [
            Path(output.splitlines()[0][dir_start_index:]).name
            for output in porcelain_output
        ]
        if checkout_dir.name not in directory_names:
            # Not sure if this is reachable.
            raise DppGitCheckoutError(repo, str(checkout_dir), defect)

    try:
        return git.Repo(checkout_dir)
    except git.exc.InvalidGitRepositoryError:
        raise DppGitCheckoutInvalidRepositoryError(repo, str(checkout_dir), defect)


def _git_am(repo: git.Repo, patches: List[str]):
    """
    Apply patches to checkout branch.
    """
    # Invoke command manually, because it seems like GitPython has a bug with updating submodules.
    if repo.submodules:
        try:
            repo.git.execute(["git", "submodule", "update", "--init"])
        except git.exc.GitError as e:
            raise DppGitSubmoduleInitError(repo, e.command, e.status, e.stderr)

    prev_hash = repo.git.rev_parse("--verify", "HEAD")
    patches = list(filter(None, patches))
    if patches:
        message.info(
            __name__, f"{', '.join(os.path.basename(patch) for patch in patches)}"
        )
    else:
        message.info(__name__, "no patches")

    for patch in patches:
        try:
            repo.git.am(patch)
        except git.GitCommandError as e:
            raise DppGitApplyPatchError(repo, patch, e.command, e.status, e.stderr)

        current_hash = repo.git.rev_parse("--verify", "HEAD")
        if prev_hash == current_hash:
            raise DppGitPatchNotAppliedError(repo, patch)
        prev_hash = current_hash


class CheckoutCommand(Command):
    """
    Checkout command which handles VCS commands based on taxonomy information.
    """

    _ERROR_MESSAGES: Dict[Type[DppGitError], str] = {
        DppGitCloneError: "git-clone failed",
        DppGitWorktreeError: "git-worktree failed",
        DppGitCheckoutInvalidRepositoryError: "git-checkout failed (not a git repository)",
        DppGitCheckoutError: "git-checkout failed",
        DppGitSubmoduleInitError: "git-submodule failed",
        DppGitApplyPatchError: "git-am failed",
        DppGitPatchNotAppliedError: "git-am patch could not be applied",
    }

    def __init__(self):
        super().__init__()
        # TODO: write argparse description in detail
        self.parser = create_common_vcs_parser()
        self.parser.usage = "bugcpp.py checkout PROJECT INDEX [-b|--buggy] [-t|--target WORKSPACE] [-s|--source-only] [-v|--verbose]"
        self.parser.description = dedent(
            """\
        Checkout defect taxonomy.
        """
        )

    def __call__(self, argv: List[str]):
        """
        Clone a repository into the given directory or checkout to a specific commit on the host machine.
        It does not perform action inside a container unlike the other commands.
        It utilizes git-worktree rather than cleaning up the current directory and checking out.
        It not only makes hoping around commits more quickly, but also reduces overhead of writing and deleting files.

        Parameters
        ----------
        argv : List[str]
            Command line argument vector.

        Returns
        -------
        None
        """
        args = self.parser.parse_args(argv)
        metadata = args.metadata
        metadata_base = args.metadata_base
        worktree = args.worktree
        # args.index is 1 based.
        defect = metadata.defects[args.index - 1]

        try:
            message.info(__name__, f"git-clone '{metadata.name}'")
            message.stdout_progress(
                f"[{metadata.name}] cloning a new repository from '{metadata.info.url}'"
            )
            repo = _git_clone(worktree.base / ".repo", metadata)

            message.info(__name__, "git-checkout")
            message.stdout_progress(f"[{metadata.name}] checking out '{defect.hash}'")
            checkout_repo = _git_checkout(repo, worktree.host, defect)

            current_hash = checkout_repo.git.rev_parse("--verify", "HEAD")
            if current_hash == defect.hash:
                message.info(__name__, "git-am")
                _git_am(
                    checkout_repo,
                    [
                        defect.common_patch,
                        defect.split_patch,
                        defect.buggy_patch if args.buggy else defect.fixed_patch,
                    ],
                )
            else:
                message.info(__name__, "git-am skipped")

            # check if there are extra data
            path_to_extra = Path(metadata_base).joinpath(
                metadata.name, "extra", f"{args.index:04}"
            )
            if path_to_extra.exists():
                message.info(
                    __name__,
                    f"copying extra directory(f{path_to_extra}) to project root",
                )
                for extra in Path.iterdir(path_to_extra):
                    shutil.copytree(
                        extra, Path(worktree.host, extra.stem), dirs_exist_ok=True
                    )

            message.info(__name__, f"creating '.defects4cpp.json' at {worktree.host}")
            # Write .defects4cpp.json in the directory.
            Project.write_config(worktree)
            if not args.source_only:
                try:
                    docker = Docker(metadata.dockerfile, worktree, verbose=args.verbose)
                    image = docker.image
                    message.info(__name__, f"    image: '{image}'")
                except Exception as e:
                    message.stdout_error(
                        f"    An API Error occured.{os.linesep}"
                        f"    Find detailed message at {message.path}."
                    )

        except DppGitError as e:
            message.error(__name__, str(e))
            message.stdout_progress_error(f"[{metadata.name}] {str(e)}")
            sys.exit(1)

        # pull docker image if it does not exist
        message.info(__name__, "pulling docker image")
        dockerfile = metadata.dockerfile
        tag = Path(dockerfile).parent.name
        self._container_name: str = f"{tag}-dpp"
        self._tag = f"hschoe/defects4cpp-ubuntu:{tag}"

        message.stdout_progress(f"[{metadata.name}] done")

    @property
    def group(self) -> str:
        return "v1"

    @property
    def help(self) -> str:
        return "Get a specific defect snapshot"
