"""Compare two projects' env contents side-by-side."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple
from envoy.storage import load_env
from envoy.crypto import decrypt


class CompareError(Exception):
    pass


@dataclass
class CompareResult:
    only_in_a: List[str] = field(default_factory=list)
    only_in_b: List[str] = field(default_factory=list)
    same: List[str] = field(default_factory=list)
    different: List[Tuple[str, str, str]] = field(default_factory=list)  # key, val_a, val_b

    @property
    def is_equal(self) -> bool:
        return not (self.only_in_a or self.only_in_b or self.different)


def _parse_pairs(text: str) -> Dict[str, str]:
    pairs: Dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        pairs[k.strip()] = v.strip().strip('"\'')
    return pairs


def compare_projects(
    project_a: str,
    password_a: str,
    project_b: str,
    password_b: str,
) -> CompareResult:
    try:
        cipher_a = load_env(project_a)
    except FileNotFoundError:
        raise CompareError(f"Project not found: {project_a}")
    try:
        cipher_b = load_env(project_b)
    except FileNotFoundError:
        raise CompareError(f"Project not found: {project_b}")

    try:
        text_a = decrypt(cipher_a, password_a)
    except Exception:
        raise CompareError(f"Failed to decrypt {project_a}: wrong password?")
    try:
        text_b = decrypt(cipher_b, password_b)
    except Exception:
        raise CompareError(f"Failed to decrypt {project_b}: wrong password?")

    pairs_a = _parse_pairs(text_a)
    pairs_b = _parse_pairs(text_b)
    keys_a, keys_b = set(pairs_a), set(pairs_b)

    result = CompareResult()
    result.only_in_a = sorted(keys_a - keys_b)
    result.only_in_b = sorted(keys_b - keys_a)
    for key in sorted(keys_a & keys_b):
        if pairs_a[key] == pairs_b[key]:
            result.same.append(key)
        else:
            result.different.append((key, pairs_a[key], pairs_b[key]))
    return result


def format_compare(result: CompareResult, a: str, b: str) -> str:
    lines = []
    for key in result.only_in_a:
        lines.append(f"< {key}  (only in {a})")
    for key in result.only_in_b:
        lines.append(f"> {key}  (only in {b})")
    for key, va, vb in result.different:
        lines.append(f"~ {key}: {a}={va!r}  {b}={vb!r}")
    if not lines:
        lines.append("Projects are identical.")
    return "\n".join(lines)
