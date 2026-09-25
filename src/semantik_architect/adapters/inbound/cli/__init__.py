"""Command-line inbound adapter.

Keep this package import side-effect free.  In particular, do not import
``.main`` here: Python imports the package before executing
``python -m semantik_architect.adapters.inbound.cli.main`` and an eager import
would preload the execution module, causing ``runpy`` to emit a RuntimeWarning.
"""

from __future__ import annotations

from typing import Any

__all__ = ["main"]


def main(*args: Any, **kwargs: Any) -> Any:
    """Invoke the CLI entry point without importing it during package import."""
    from .main import main as _main

    return _main(*args, **kwargs)
