import multiprocessing
import sys
import time

import lib.debug as debug
import message
import processor


def display_general_usage():
    message.kind("Usage:")
    message.command("    d++ command [command option]")
    message.blank()
    message.kind("These are d++ commands used in various situations:")
    a = processor.Action()
    for cmd in a.commands:
        message.command(f"    {cmd:<10}\t{getattr(a, cmd).help}")
    message.blank()


def main_driver():
    a = processor.Action()

    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command in a.commands:
            # return commands[sys.argv[1]]["function"]()
            pass
        else:
            message.error(f"'{command}' is not a valid command")
    else:
        message.kind("Defects4C++: Defect Taxonomies for Automated-Debugging")
        message.kind("MIT Licensed, Suresoft Technologies Inc.")
        message.blank()
        display_general_usage()


if __name__ == "__main__":
    multiprocessing.freeze_support()
    start_time = time.time()
    try:
        main_driver()
    except:
        traceback_msg = debug.get_trace_back()
        message.error(traceback_msg)
    finally:
        sys.exit(0)
