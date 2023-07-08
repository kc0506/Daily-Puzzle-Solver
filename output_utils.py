import os
import platform


def clear():
    if platform.system() == "Windows":
        os.system("cls")
    else:  # Linux and Mac
        print("\033c", end="")


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"




from colorama import Fore, Style

PALLATES = [
    Fore.BLUE,
    Fore.CYAN,
    Fore.GREEN,
    Fore.YELLOW,
    Fore.RED,
    Fore.MAGENTA,
    Fore.LIGHTRED_EX,
    Fore.LIGHTYELLOW_EX,
    Fore.LIGHTBLACK_EX,
    Fore.LIGHTGREEN_EX,
]
RESET_COLOR = Style.RESET_ALL
