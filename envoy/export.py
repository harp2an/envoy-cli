"""Export and import .env files in various formats."""

from __future__ import annotations

import re
from typing import Dict


class ExportError(Exception):
    pass


def parse_dotenv(text: str) -> Dict[str, str]:
    """Parse a .env file text into a key/value dict."""
    result: Dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise ExportError(f"Invalid line in .env: {line!r}")
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        # Strip optional surrounding quotes
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
            value = value[1:-1]
        if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", key):
            raise ExportError(f"Invalid key name: {key!r}")
        result[key] = value
    return result


def render_dotenv(env: Dict[str, str]) -> str:
    """Render a key/value dict as .env file text."""
    lines = []
    for key, value in sorted(env.items()):
        # Quote values that contain spaces or special characters
        if any(c in value for c in (" ", "#", "'", '"', "\n")):
            escaped = value.replace('"', '\\"')
            lines.append(f'{key}="{escaped}"')
        else:
            lines.append(f"{key}={value}")
    return "\n".join(lines) + ("\n" if lines else "")


def export_shell(env: Dict[str, str]) -> str:
    """Render env vars as shell export statements."""
    lines = []
    for key, value in sorted(env.items()):
        escaped = value.replace('"', '\\"')
        lines.append(f'export {key}="{escaped}"')
    return "\n".join(lines) + ("\n" if lines else "")
