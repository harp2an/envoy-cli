"""Template support: generate .env files from a template with variable substitution."""

import re
from typing import Dict, Optional

TEMPLATE_VAR_RE = re.compile(r"\{\{\s*(\w+)\s*\}\}")


class TemplateError(Exception):
    pass


def parse_template(text: str) -> list[str]:
    """Return list of variable names found in template."""
    return list(dict.fromkeys(TEMPLATE_VAR_RE.findall(text)))


def render_template(template: str, variables: Dict[str, str], strict: bool = True) -> str:
    """Render a .env template, substituting {{ VAR }} placeholders.

    If strict=True, raises TemplateError for any unresolved variable.
    """
    missing = [v for v in parse_template(template) if v not in variables]
    if strict and missing:
        raise TemplateError(f"Missing template variables: {', '.join(missing)}")

    def replacer(m: re.Match) -> str:
        key = m.group(1)
        return variables.get(key, m.group(0))

    return TEMPLATE_VAR_RE.sub(replacer, template)


def load_template_file(path: str) -> str:
    """Read a template file from disk."""
    try:
        with open(path, "r") as f:
            return f.read()
    except FileNotFoundError:
        raise TemplateError(f"Template file not found: {path}")


def apply_template_to_project(
    template_text: str,
    variables: Dict[str, str],
    strict: bool = True,
) -> str:
    """High-level helper: render and return final .env content."""
    return render_template(template_text, variables, strict=strict)
