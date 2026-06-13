"""Lint rules for Agent Skills.

Each rule is a function (skills, root) -> list[Finding]. Rules are intentionally
small and independent so they're easy to test and extend.
"""
from __future__ import annotations

import re
from pathlib import Path

from .core import Finding, Severity, SkillFile

# --------------------------------------------------------------------------
# Rule 1: frontmatter validity
# --------------------------------------------------------------------------

# valid skill name per the Agent Skills convention: lowercase, hyphen/underscore
_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")
_MAX_DESC = 1024


def rule_frontmatter(skills: list[SkillFile], root: Path) -> list[Finding]:
    out = []
    for s in skills:
        if s.parse_error:
            out.append(Finding("frontmatter", Severity.ERROR,
                               f"cannot parse frontmatter: {s.parse_error}",
                               path=s.path, skill=s.name))
            continue
        fm = s.frontmatter
        name = fm.get("name")
        if not name or not isinstance(name, str) or not name.strip():
            out.append(Finding("frontmatter.name", Severity.ERROR,
                               "missing required field 'name'",
                               path=s.path, skill=s.name))
        elif not _NAME_RE.match(name.strip()):
            out.append(Finding("frontmatter.name", Severity.WARN,
                               f"name '{name}' should be lowercase letters/digits/"
                               "hyphens/underscores, <=64 chars",
                               path=s.path, skill=s.name))
        desc = fm.get("description")
        if not desc or not isinstance(desc, str) or not desc.strip():
            out.append(Finding("frontmatter.description", Severity.ERROR,
                               "missing required field 'description'",
                               path=s.path, skill=s.name))
        elif len(desc) > _MAX_DESC:
            out.append(Finding("frontmatter.description", Severity.WARN,
                               f"description is {len(desc)} chars (>{_MAX_DESC}); "
                               "keep it short so it's cheap to preload",
                               path=s.path, skill=s.name))
    return out


# --------------------------------------------------------------------------
# Rule 2: duplicate skill names
# --------------------------------------------------------------------------

def rule_duplicates(skills: list[SkillFile], root: Path) -> list[Finding]:
    out = []
    seen: dict[str, list[Path]] = {}
    for s in skills:
        if s.parse_error:
            continue
        nm = (s.frontmatter.get("name") or "").strip().lower()
        if nm:
            seen.setdefault(nm, []).append(s.path)
    for nm, paths in seen.items():
        if len(paths) > 1:
            locs = ", ".join(str(p) for p in paths)
            out.append(Finding("duplicate-name", Severity.ERROR,
                               f"name '{nm}' declared in {len(paths)} skills: {locs}",
                               path=paths[0], skill=nm))
    return out


# --------------------------------------------------------------------------
# Rule 3: leaked secrets inside skill files
# --------------------------------------------------------------------------

_SECRET_PATTERNS = [
    ("aws_access_key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("openai_key", re.compile(r"\bsk-[A-Za-z0-9]{20,}\b")),
    ("github_pat", re.compile(r"\bghp_[A-Za-z0-9]{30,}\b")),
    ("github_fine_grained", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{50,}\b")),
    ("google_api_key", re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b")),
    ("slack_token", re.compile(r"\bxox[baprs]-[0-9A-Za-z\-]{10,}\b")),
    ("jwt", re.compile(r"\beyJ[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+\b")),
    ("pem_private_key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("hex_private_key", re.compile(r"\b0x[a-fA-F0-9]{64}\b")),
    ("generic_secret_assign", re.compile(
        r"(?i)\b(api[_-]?key|secret|token|password|passwd)\b\s*[:=]\s*"
        r"['\"][A-Za-z0-9_\-]{16,}['\"]")),
]


def rule_secrets(skills: list[SkillFile], root: Path) -> list[Finding]:
    out = []
    for s in skills:
        for kind, rx in _SECRET_PATTERNS:
            for m in rx.finditer(s.raw):
                line = s.raw.count("\n", 0, m.start()) + 1
                out.append(Finding("secret", Severity.ERROR,
                                   f"possible leaked secret ({kind}) at line {line}",
                                   path=s.path, skill=s.name))
                break  # one finding per pattern per file is enough
    return out


# --------------------------------------------------------------------------
# Rule 4: description quality (helps the router disambiguate)
# --------------------------------------------------------------------------

_GENERIC_DESC = re.compile(
    r"^(a skill (that|for|to)|this skill|helps? (you )?with|tool for)\b", re.I)


def rule_description_quality(skills: list[SkillFile], root: Path) -> list[Finding]:
    out = []
    for s in skills:
        if s.parse_error:
            continue
        desc = (s.frontmatter.get("description") or "").strip()
        if not desc:
            continue
        if len(desc) < 20:
            out.append(Finding("description.short", Severity.WARN,
                               f"description is very short ({len(desc)} chars); "
                               "the router needs detail to pick this skill",
                               path=s.path, skill=s.name))
        if _GENERIC_DESC.match(desc):
            out.append(Finding("description.generic", Severity.INFO,
                               "description starts generically; lead with concrete "
                               "trigger conditions ('Use when ...')",
                               path=s.path, skill=s.name))
    return out


# --------------------------------------------------------------------------
# Rule 5: trigger collisions (ambiguous router) — borrowed from router-tie-test
# --------------------------------------------------------------------------

_STOPWORDS = {
    "the", "a", "an", "to", "for", "of", "and", "or", "with", "use", "when",
    "this", "that", "skill", "using", "via", "from", "into", "your", "you",
    "it", "is", "are", "be", "on", "in", "by", "as", "at",
}


def _keywords(desc: str) -> set[str]:
    words = re.findall(r"[a-zA-Z][a-zA-Z0-9_-]{2,}", desc.lower())
    return {w for w in words if w not in _STOPWORDS}


def rule_trigger_collisions(skills: list[SkillFile], root: Path,
                            threshold: float = 0.6) -> list[Finding]:
    """Flag skill pairs whose descriptions share a high fraction of keywords —
    the router will struggle to disambiguate them (the 'nyangkut' problem)."""
    out = []
    kw = []
    for s in skills:
        if s.parse_error:
            continue
        desc = (s.frontmatter.get("description") or "")
        ks = _keywords(desc)
        if ks:
            kw.append((s, ks))
    for i in range(len(kw)):
        for j in range(i + 1, len(kw)):
            s_a, a = kw[i]
            s_b, b = kw[j]
            inter = a & b
            union = a | b
            if not union:
                continue
            jacc = len(inter) / len(union)
            if jacc >= threshold:
                shared = ", ".join(sorted(inter)[:6])
                out.append(Finding("trigger-collision", Severity.WARN,
                                   f"'{s_a.name}' and '{s_b.name}' share "
                                   f"{jacc:.0%} of trigger keywords ({shared}); "
                                   "router may tie between them",
                                   path=s_a.path, skill=s_a.name))
    return out


ALL_RULES = [
    rule_frontmatter,
    rule_duplicates,
    rule_secrets,
    rule_description_quality,
    rule_trigger_collisions,
]
