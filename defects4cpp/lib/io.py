import os
import colorama
from colorama import Fore

colorama.init()


def kindness_message(message):
    print("%s> %s%s" % (Fore.GREEN, message, Fore.RESET))


def warning_message(message, log_path=None):
    print("%s   -- %s%s" % (Fore.YELLOW, message, Fore.RESET))


def error_message(message):
    print("%s   !! %s !!%s" % (Fore.RED, message, Fore.RESET))


def command_message(message):
    print("%s%s%s" % (Fore.YELLOW, message, Fore.RESET))


def info_message(message):
    print("  > %s%s%s" % (Fore.CYAN, message, Fore.RESET))


def info2_message(message):
    print("    > %s%s%s" % (Fore.LIGHTCYAN_EX, message, Fore.RESET))


def step_message(message):
    print("-- %s[%s]%s" % (Fore.YELLOW, message, Fore.RESET))


def blank():
    print("")


"""
Directory which d++.py is placed
"""
DPP_HOME: str = os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))
