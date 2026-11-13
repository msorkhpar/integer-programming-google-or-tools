"""python -m renewal: the same as the `renewal` command."""

import sys

from .cli import main

if __name__ == "__main__":
    sys.exit(main())
