"""
Helper entry point to run MutPy with a deterministic multiprocessing start method.

On macOS and Python 3.8+, the default start method for multiprocessing is ``spawn``.
MutPy relies on memory sharing between processes to inject mutant modules, which
works reliably with ``fork`` but not with ``spawn``.  By forcing ``fork`` we ensure
that mutant modules propagate correctly to the test runner process.
"""

from __future__ import annotations

import multiprocessing as mp
import sys

from mutpy import commandline


def main(argv: list[str] | None = None) -> None:
    argv = sys.argv if argv is None else argv
    try:
        mp.set_start_method("fork")
    except RuntimeError:
        # Start method already set – nothing else to do.
        pass

    commandline.main(argv)


if __name__ == "__main__":
    main()
