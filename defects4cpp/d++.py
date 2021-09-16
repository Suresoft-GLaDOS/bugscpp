import sys
import time

import lib.debug as debug
import message
import processor


def main():
    def measure_time(func, args):
        start_time = time.time()
        func(args)
        elapsed = time.time() - start_time
        if elapsed < 100:
            message.info(f"Elapsed: {elapsed:.2f}s")
        else:
            minutes, seconds = divmod(elapsed, 60)
            message.info(f"Elapsed: {int(minutes)}m {seconds:.2f}s")

    commands = processor.CommandList()

    try:
        name = sys.argv[1]
    except IndexError:
        name = "help"

    argv = sys.argv[2:]
    if name not in commands.keys():
        message.error(f"'{name}' is not a valid command")
        return 1

    try:
        if name != "help":
            measure_time(commands[name], argv)
        else:
            commands[name](argv)
    except SystemExit:
        pass
    except:
        traceback_msg = debug.get_trace_back()
        message.error(traceback_msg)
        return 2
    else:
        return 0


if __name__ == "__main__":
    from multiprocessing import freeze_support

    freeze_support()

    main()
