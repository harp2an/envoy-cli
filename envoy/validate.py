"""Validate .env content against a schema of required and optional keys."""

from dataclasses import dataclass, field
from typing import List, Optional


class ValidationError(Exception):
    pass


@dataclass
class ValidationResult:
    missing: List[str] = field(default_factory=list)
    unknown: List[str] = field(default_factory=list)
    empty: List[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not (self.missing or self.unknown or self.empty)

    def __str__(self) -> str:
        lines = []
        for k in self.missing:
            lines.append(f"  MISSING   {k}")
        for k in self.empty:
            lines.append(f"  EMPTY     {k}")
        for k in self.unknown:
            lines.append(f"  UNKNOWN   {k}")
        return "\n".join(lines) if lines else "OK"


def _parse_pairs(content: str) -> dict:
    pairs = {}
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        k, _, v = line.partition("=")
        pairs[k.strip()] = v.strip()
    return pairs


def validate_env(
    content: str,
    required: List[str],
    optional: Optional[List[str]] = None,
    allow_unknown: bool = True,
    allow_empty: bool = True,
) -> ValidationResult:
    pairs = _parse_pairs(content)
    result = ValidationResult()

    for key in required:
        if key not in pairs:
            result.missing.append(key)
        elif not allow_empty and pairs[key] == "":
            result.empty.append(key)

    if not allow_unknown and optional is not None:
        allowed = set(required) | set(optional)
        for key in pairs:
            if key not in allowed:
                result.unknown.append(key)

    return result
