
GRAY = '\033[{0};30m'
RED = '\033[{0};31m'
GREEN = '\033[{0};32m'
YELLOW = '\033[{0};33m'
BLUE = '\033[{0};34m'
MAGENTA = '\033[{0};35m'
CYAN = '\033[{0};36m'
WHITE = '\033[{0};37m'
LIGHTGRAY = '\033[{0};90m'
LIGHTRED = '\033[{0};91m'
LIGHTGREEN = '\033[{0};92m'
LIGHTYELLOW = '\033[{0};93m'
LIGHTBLUE = '\033[{0};94m'
LIGHTMAGENTA = '\033[{0};95m'
LIGHTCYAN = '\033[{0};96m'
LIGHTWHITE = '\033[{0};97m'
ENDC = '\033[0m'


def echo(text, color=None, bold=True, printit=True):
    endc = ENDC
    color = color.format(1) if bold and color is not None else color.format(0)
    if color is None:
        color, endc = '', ''

    if printit:
        print '{0}{1}{2}'.format(color, text, endc)
    else:
        return '{0}{1}{2}'.format(color, text, endc)


if __name__ == '__main__':
    color_list = (
        GRAY,
        RED,
        GREEN,
        YELLOW,
        BLUE,
        MAGENTA,
        CYAN,
        WHITE,
        LIGHTGRAY,
        LIGHTRED,
        LIGHTGREEN,
        LIGHTYELLOW,
        LIGHTBLUE,
        LIGHTMAGENTA,
        LIGHTCYAN,
        LIGHTWHITE,
    )

    print 'Non bold colors'
    for color in color_list:
        echo('COLOR TEST', color, bold=False)

    print
    print 'Bold colors'
    for color in color_list:
        echo('COLOR TEST', color, bold=True)