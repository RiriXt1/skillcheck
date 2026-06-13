"""Output formatting: pretty terminal report + JSON."""
from __future__ import annotations

import json
from pathlib import Path

from .core import Finding, Severity, SkillFile

_ICON = {Severity.ERROR: "✗", Severity.WARN: "!", Severity.INFO: "·"}
_COLOR = {Severity.ERROR: "\033[31m", Severity.WARN: "\033[33m", Severity.INFO: "\033[36m"}
_RESET = "\033[0m"


def _c(text: str, sev: Severity, color: bool) -> str:
    if not color:
        return text
    return f"{_COLOR[sev]}{text}{_RESET}"


def render_text(skills: list[SkillFile], findings: list[Finding],
                root: Path, color: bool = True) -> str:
    lines = []
    n_err = sum(1 for f in findings if f.severity == Severity.ERROR)
    n_warn = sum(1 for f in findings if f.severity == Severity.WARN)
    n_info = sum(1 for f in findings if f.severity == Severity.INFO)

    # group findings by file
    by_path: dict[str, list[Finding]] = {}
    for f in findings:
        by_path.setdefault(str(f.path or "(global)"), []).append(f)

    for path, fs in by_path.items():
        try:
            rel = Path(path).relative_to(root) if Path(path).is_absolute() else Path(path)
        except (ValueError, OSError):
            rel = Path(path)
        lines.append(f"\n  {rel}")
        for f in fs:
            icon = _c(_ICON[f.severity], f.severity, color)
            lines.append(f"    {icon} {f.rule}: {f.message}")

    lines.append("")
    lines.append(f"  scanned {len(skills)} skill(s)")
    summary = (f"  {n_err} error(s), {n_warn} warning(s), {n_info} info")
    if n_err:
        summary = _c(summary, Severity.ERROR, color)
    elif n_warn:
        summary = _c(summary, Severity.WARN, color)
    else:
        summary = _c("  all clear ✓", Severity.INFO, color) if not findings else summary
    lines.append(summary)
    return "\n".join(lines)


def render_json(skills: list[SkillFile], findings: list[Finding], root: Path) -> str:
    payload = {
        "root": str(root),
        "scanned": len(skills),
        "summary": {
            "error": sum(1 for f in findings if f.severity == Severity.ERROR),
            "warn": sum(1 for f in findings if f.severity == Severity.WARN),
            "info": sum(1 for f in findings if f.severity == Severity.INFO),
        },
        "findings": [f.as_dict() for f in findings],
    }
    return json.dumps(payload, indent=2)
