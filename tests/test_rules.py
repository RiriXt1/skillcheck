"""Tests for skillcheck rules. Each fixture is deliberately broken so we prove
the rule actually fires (anti-false-confidence)."""
from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from skillcheck.core import SkillFile, lint_path
from skillcheck import rules


def _write_skill(dir_: Path, name: str, frontmatter: str, body: str = "Body.") -> Path:
    d = dir_ / name
    d.mkdir(parents=True, exist_ok=True)
    p = d / "SKILL.md"
    p.write_text(f"---\n{textwrap.dedent(frontmatter).strip()}\n---\n\n{body}\n",
                 encoding="utf-8")
    return p


# --- frontmatter ----------------------------------------------------------

def test_missing_name(tmp_path):
    _write_skill(tmp_path, "a", "description: A clear description of the thing.")
    _, findings = lint_path(tmp_path)
    assert any(f.rule == "frontmatter.name" and f.severity.label() == "error"
               for f in findings)


def test_missing_description(tmp_path):
    _write_skill(tmp_path, "a", "name: alpha")
    _, findings = lint_path(tmp_path)
    assert any(f.rule == "frontmatter.description" for f in findings)


def test_bad_name_format(tmp_path):
    _write_skill(tmp_path, "a", "name: Bad Name!!!\ndescription: long enough description here")
    _, findings = lint_path(tmp_path)
    assert any(f.rule == "frontmatter.name" for f in findings)


def test_no_frontmatter(tmp_path):
    d = tmp_path / "raw"
    d.mkdir()
    (d / "SKILL.md").write_text("# just a heading\n\nno frontmatter", encoding="utf-8")
    _, findings = lint_path(tmp_path)
    assert any(f.rule == "frontmatter" and f.severity.label() == "error"
               for f in findings)


def test_clean_skill_passes(tmp_path):
    _write_skill(tmp_path, "good",
                 "name: good-skill\ndescription: Use when converting CSV files to "
                 "Parquet with schema validation and compression options.")
    skills, findings = lint_path(tmp_path)
    assert len(skills) == 1
    assert not any(f.severity.label() == "error" for f in findings)


# --- duplicates -----------------------------------------------------------

def test_duplicate_names(tmp_path):
    _write_skill(tmp_path, "one", "name: dupe\ndescription: first description that is long enough")
    _write_skill(tmp_path, "two", "name: dupe\ndescription: second description that is long enough")
    _, findings = lint_path(tmp_path)
    assert any(f.rule == "duplicate-name" for f in findings)


# --- secrets --------------------------------------------------------------

def test_secret_aws_key(tmp_path):
    _write_skill(tmp_path, "leaky",
                 "name: leaky\ndescription: a skill that leaks an aws key in the body text",
                 body="here is a key AKIAIOSFODNN7EXAMPLE oops")
    _, findings = lint_path(tmp_path)
    assert any(f.rule == "secret" for f in findings)


def test_secret_openai_key(tmp_path):
    fake = "sk-" + "a" * 40
    _write_skill(tmp_path, "leaky2",
                 "name: leaky2\ndescription: description long enough to pass checks",
                 body=f"token: {fake}")
    _, findings = lint_path(tmp_path)
    assert any(f.rule == "secret" for f in findings)


# --- trigger collisions ---------------------------------------------------

def test_trigger_collision(tmp_path):
    _write_skill(tmp_path, "pdf-a",
                 "name: pdf-merge\ndescription: merge combine pdf documents files pages into one")
    _write_skill(tmp_path, "pdf-b",
                 "name: pdf-join\ndescription: combine merge pdf documents files pages together")
    _, findings = lint_path(tmp_path)
    assert any(f.rule == "trigger-collision" for f in findings), \
        "near-identical descriptions should collide"


def test_no_collision_for_distinct(tmp_path):
    _write_skill(tmp_path, "music",
                 "name: music\ndescription: synthesize vocaloid singing melody lyrics audio")
    _write_skill(tmp_path, "deploy",
                 "name: deploy\ndescription: provision kubernetes nginx docker servers via ssh")
    _, findings = lint_path(tmp_path)
    assert not any(f.rule == "trigger-collision" for f in findings)


# --- discovery ------------------------------------------------------------

def test_single_file_input(tmp_path):
    p = _write_skill(tmp_path, "solo", "name: solo\ndescription: a long enough description for solo")
    skills, _ = lint_path(p)
    assert len(skills) == 1
