"""Lint .env content for common issues."""

from dataclasses import dataclass, field
from typing import List


class LintError(Exception):
    pass


@dataclass
class LintIssue:
    line: int
    code: str
    message: str

    def __str__(self) -> str:
        return f"L{self.line} [{self.code}] {self.message}"


@dataclass
class LintResult:
    issues: List[LintIssue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.issues) == 0


def lint_content(content: str) -> LintResult:
    result = LintResult()
    seen_keys: dict = {}

    for lineno, raw in enumerate(content.splitlines(), start=1):
        line = raw.strip()

        if not line or line.startswith("#"):
            continue

        if "=" not in line:
            result.issues.append(LintIssue(lineno, "E001", f"Invalid line (no '='): {raw!r}"))
            continue

        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()

        if not key:
            result.issues.append(LintIssue(lineno, "E002", "Empty key"))
            continue

        if not key.replace("_", "").isalnum() or key[0].isdigit():
            result.issues.append(LintIssue(lineno, "W001", f"Unconventional key name: {key!r}"))

        if key in seen_keys:
            result.issues.append(LintIssue(lineno, "W002", f"Duplicate key: {key!r} (first at L{seen_keys[key]})"))
        else:
            seen_keys[key] = lineno

        if not value:
            result.issues.append(LintIssue(lineno, "W003", f"Empty value for key: {key!r}"))

    return result


def lint_project(project: str, password: str) -> LintResult:
    from envoy.storage import load_env
    try:
        content = load_env(project, password)
    except Exception as exc:
        raise LintError(f"Could not load project {project!r}: {exc}") from exc
    return lint_content(content)
