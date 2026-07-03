"""Tests for description quality and generic description detection."""
from __future__ import annotations

from pathlib import Path

from skillcheck.core import SkillFile, lint_path
from skillcheck import rules


def _write_skill(dir_: Path, name: str, frontmatter: str, body: str = "Body.") -> Path:
    import textwrap
    d = dir_ / name
    d.mkdir(parents=True, exist_ok=True)
    p = d / "SKILL.md"
    p.write_text(f"---\n{textwrap.dedent(frontmatter).strip()}\n---\n\n{body}\n",
                 encoding="utf-8")
    return p


def test_generic_description_starts_with_a_skill(tmp_path):
    """Descriptions starting with 'a skill that...' trigger INFO finding."""
    _write_skill(tmp_path, "generic",
                 "name: generic-skill\ndescription: A skill that helps you write code.")
    _, findings = lint_path(tmp_path)
    assert any(f.rule == "description.generic" for f in findings), \
        "descriptions starting with 'a skill that' should be flagged"


def test_good_description_no_generic_warning(tmp_path):
    """Concrete descriptions like 'Use when ...' should not trigger generic."""
    _write_skill(tmp_path, "good",
                 "name: good-skill\ndescription: Use when converting CSV to Parquet.")
    _, findings = lint_path(tmp_path)
    assert not any(f.rule == "description.generic" for f in findings), \
        "concrete descriptions should not be flagged as generic"


def test_short_description_warns(tmp_path):
    """Descriptions under 20 chars should trigger a WARN."""
    _write_skill(tmp_path, "short",
                 "name: short-skill\ndescription: tiny")
    _, findings = lint_path(tmp_path)
    assert any(f.rule == "description.short" and f.severity.label() == "warn"
               for f in findings), \
        "very short descriptions should warn"


def test_severity_ordering():
    """Severity should be ordered: INFO < WARN < ERROR."""
    from skillcheck.core import Severity
    assert Severity.INFO < Severity.WARN < Severity.ERROR
    assert int(Severity.INFO) == 0
    assert int(Severity.WARN) == 1
    assert int(Severity.ERROR) == 2
