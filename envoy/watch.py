"""Watch a .env file for changes and auto-sync to storage."""

import time
import os
from pathlib import Path
from typing import Callable, Optional


class WatchError(Exception):
    pass


def _mtime(path: Path) -> float:
    try:
        return path.stat().st_mtime
    except FileNotFoundError:
        return 0.0


def watch_file(
    path: Path,
    on_change: Callable[[Path], None],
    interval: float = 1.0,
    max_iterations: Optional[int] = None,
) -> None:
    """Poll *path* and call *on_change* whenever its mtime changes.

    Args:
        path: File to watch.
        on_change: Callback invoked with the path when a change is detected.
        interval: Polling interval in seconds.
        max_iterations: Stop after this many iterations (None = run forever).
    """
    if not isinstance(path, Path):
        path = Path(path)

    last_mtime = _mtime(path)
    iterations = 0

    while max_iterations is None or iterations < max_iterations:
        time.sleep(interval)
        current_mtime = _mtime(path)
        if current_mtime != last_mtime:
            last_mtime = current_mtime
            on_change(path)
        iterations += 1


def make_store_callback(project: str, password: str) -> Callable[[Path], None]:
    """Return a callback that stores the env file content on change."""
    from envoy.storage import store_env

    def _callback(path: Path) -> None:
        content = path.read_text(encoding="utf-8")
        store_env(project, content, password)

    return _callback
