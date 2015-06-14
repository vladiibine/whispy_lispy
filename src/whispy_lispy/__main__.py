# coding -*- utf-8 -*-
from __future__ import unicode_literals
import sys
# Why does this file exist, and why __main__?
# For more info, read:
# - https://www.python.org/dev/peps/pep-0338/
# - https://docs.python.org/2/using/cmdline.html#cmdoption-m
# - https://docs.python.org/3/using/cmdline.html#cmdoption-m
from whispy_lispy import skip_steps, repl


def main(argv=()):
    """
    Args:
        argv (list): List of arguments

    Returns:
        int: A return code

    Does stuff.
    """
    if argv[1] == '-r':
        repl.repl()
    else:
        skip_steps.interpret_text2(argv[1])
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
