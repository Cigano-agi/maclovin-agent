"""Package entry point for `python -m maclovin`."""

import sys
import io

# Garantir UTF-8 no stdout/stderr no Windows
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from maclovin.cli import main

if __name__ == "__main__":
    main()
