import colorama
from colorama import Fore

colorama.init()


def kind(message: str):
    print(f"{Fore.GREEN}> {message}{Fore.RESET}")


def warning(message: str, log_path=None):
    print(f"{Fore.YELLOW}   -- {message}{Fore.RESET}")


def error(message: str):
    print(f"{Fore.RED}   !! {message} !!{Fore.RESET}")


def command(message: str):
    print(f"{Fore.YELLOW}{message}{Fore.RESET}")


def info(message: str):
    print(f"  > {Fore.CYAN}{message}{Fore.RESET}")


def info2(message: str):
    print(f"    > {Fore.LIGHTCYAN_EX}{message}{Fore.RESET}")


def step(message: str):
    print(f"-- {Fore.YELLOW}[{message}]{Fore.RESET}")


def blank():
    print("")
