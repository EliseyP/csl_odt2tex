class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    GREEN = '\033[32m'
    OKGREEN = '\033[92m'
    YELLOW = '\033[33m'
    CIAN = '\033[36m'
    LCIAN = '\033[96m'
    WARNING = '\033[93m'  # Light Yellow
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


OKGREEN = bcolors.OKGREEN
GREEN = bcolors.GREEN
FAIL = bcolors.FAIL
ENDC = bcolors.ENDC
OKBLUE = bcolors.OKBLUE
LCIAN = bcolors.LCIAN

COLOR_NO = f'{bcolors.FAIL}NO{bcolors.ENDC}'
COLOR_OK = f'{bcolors.OKGREEN}OK{bcolors.ENDC}'
COLOR_PLUS_PAR = f'{bcolors.OKGREEN}[+]{bcolors.ENDC}'
COLOR_EXISTS = f'{bcolors.FAIL}EXISTS{bcolors.ENDC}'
COLOR_NOT_EXISTS = f'{bcolors.FAIL}NOT EXISTS{bcolors.ENDC}'
COLOR_MINUS_PAR = f'{bcolors.FAIL}[-]{bcolors.ENDC}'
COLOR_EXLAM_MARK_PAR = f'{bcolors.FAIL}[!]{bcolors.ENDC}'
COLOR_EXLAM_MARK = f'{bcolors.FAIL}!{bcolors.ENDC}'