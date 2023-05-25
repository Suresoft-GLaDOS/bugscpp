import sys
from time import perf_counter

from command import CommandList
from errors import DppArgparseError, DppDockerError, DppError, DppNoSuchTagError, DppSearchError
from message import message


def _handle_cmdline_error(e: DppError):
    if isinstance(e, DppArgparseError):
        message.stdout_argparse_error(str(e))
    elif isinstance(e, DppDockerError):
        message.stdout_argparse_error(str(e))
    elif isinstance(e, DppSearchError):
        message.stdout_search_error(str(e))


def main():
    def measure_time(func, args):
        start_time = perf_counter()
        func(args)
        elapsed = perf_counter() - start_time
        if elapsed < 100:
            message.stdout_progress(f"Elapsed: {elapsed:.2f}s")
        else:
            minutes, seconds = divmod(elapsed, 60)
            message.stdout_progress(f"Elapsed: {int(minutes)}m {seconds:.2f}s")

    commands = CommandList()

    try:
        name = sys.argv[1]
    except IndexError:
        name = "help"

    argv = sys.argv[2:]
    if name not in commands:
        message.stdout_progress_error(f"'{name}' is not a valid command")
        return 1

    try:
        if name not in ["help", "search"]:
            measure_time(commands[name], argv)
        else:
            commands[name](argv)
    except DppError as e:
        _handle_cmdline_error(e)


if __name__ == "__main__":
    from multiprocessing import freeze_support

    freeze_support()

    main()
