"""Core data models, SKILL.md discovery/parsing, and the lint orchestrator."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import IntEnum
from pathlib import Path
from typing import Optional

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


class Severity(IntEnum):
    """Ordered so we can threshold (e.g. fail on >= WARN)."""
    INFO = 0
    WARN = 1
    ERROR = 2

    def label(self) -> str:
        return {0: "info", 1: "warn", 2: "error"}[int(self)]


@dataclass
class Finding:
    rule: str
    severity: Severity
    message: str
    path: Optional[Path] = None
    skill: Optional[str] = None

    def as_dict(self) -> dict:
        return {
            "rule": self.rule,
            "severity": self.severity.label(),
            "message": self.message,
            "path": str(self.path) if self.path else None,
            "skill": self.skill,
        }


# --- frontmatter ----------------------------------------------------------

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*(?:\n|$)", re.DOTALL)


@dataclass
class SkillFile:
    """A parsed SKILL.md."""
    path: Path
    raw: str
    frontmatter: dict = field(default_factory=dict)
    body: str = ""
    parse_error: Optional[str] = None

    @property
    def name(self) -> str:
        fm_name = self.frontmatter.get("name")
        if isinstance(fm_name, str) and fm_name.strip():
            return fm_name.strip()
        # fall back to parent directory name
        return self.path.parent.name

    @classmethod
    def load(cls, path: Path) -> "SkillFile":
        raw = path.read_text(encoding="utf-8", errors="replace")
        m = _FRONTMATTER_RE.match(raw)
        if not m:
            return cls(path=path, raw=raw, body=raw,
                       parse_error="no YAML frontmatter block")
        fm_text, body = m.group(1), raw[m.end():]
        if yaml is None:  # pragma: no cover
            return cls(path=path, raw=raw, body=body,
                       parse_error="PyYAML not installed")
        try:
            data = yaml.safe_load(fm_text) or {}
            if not isinstance(data, dict):
                return cls(path=path, raw=raw, body=body,
                           parse_error="frontmatter is not a mapping")
            return cls(path=path, raw=raw, frontmatter=data, body=body)
        except yaml.YAMLError as e:
            return cls(path=path, raw=raw, body=body,
                       parse_error=f"YAML error: {e}")


def discover(root: Path) -> list[Path]:
    """Find every SKILL.md under root (case-insensitive). A single SKILL.md
    path is also accepted."""
    if root.is_file():
        return [root]
    out = []
    for p in root.rglob("*"):
        if p.is_file() and p.name.lower() == "skill.md":
            out.append(p)
    return sorted(out)


def lint_path(root: Path, rules=None) -> tuple[list[SkillFile], list[Finding]]:
    """Discover + parse + run all rules. Returns (skills, findings)."""
    from . import rules as rules_mod

    rule_fns = rules or rules_mod.ALL_RULES
    paths = discover(root)
    skills = [SkillFile.load(p) for p in paths]

    findings: list[Finding] = []
    for rule in rule_fns:
        findings.extend(rule(skills, root))
    # stable ordering: by severity desc, then path
    findings.sort(key=lambda f: (-int(f.severity), str(f.path or ""), f.rule))
    return skills, findings
