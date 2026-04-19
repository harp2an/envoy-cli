"""Import .env files into envoy storage."""

from pathlib import Path
from envoy.export import parse_dotenv, render_dotenv, ExportError
from envoy.storage import store_env
from envoy.audit import record_event


class ImportError(Exception):
    pass


def _validate_path(filepath: str) -> Path:
    """Validate that the given filepath exists and is a regular file."""
    path = Path(filepath)
    if not path.exists():
        raise ImportError(f"File not found: {filepath}")
    if not path.is_file():
        raise ImportError(f"Not a file: {filepath}")
    return path


def import_dotenv_file(project: str, filepath: str, password: str) -> int:
    """Read a .env file, validate it, and store it encrypted.

    Returns the number of key/value pairs imported.

    Raises:
        ImportError: If the file does not exist, is not a regular file,
            or cannot be parsed as a valid .env file.
    """
    path = _validate_path(filepath)

    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ImportError(f"Could not read file: {exc}") from exc

    try:
        pairs = parse_dotenv(raw)
    except ExportError as exc:
        raise ImportError(f"Parse error: {exc}") from exc

    content = render_dotenv(pairs)
    store_env(project, content, password)
    record_event("import", project, {"source": str(path.resolve()), "keys": len(pairs)})
    return len(pairs)
