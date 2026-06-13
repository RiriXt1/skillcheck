"""skillcheck command-line interface."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .core import Severity, lint_path
from .report import render_json, render_text

_THRESHOLD = {"error": Severity.ERROR, "warn": Severity.WARN, "info": Severity.INFO}


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="skillcheck",
        description="Lint Agent Skills (SKILL.md): frontmatter, secrets, "
                    "duplicates, and ambiguous router triggers.",
    )
    p.add_argument("path", nargs="?", default=".",
                   help="directory to scan (recursively) or a single SKILL.md "
                        "(default: current dir)")
    p.add_argument("--json", action="store_true", help="emit JSON instead of text")
    p.add_argument("--fail-on", choices=["error", "warn", "info"], default="error",
                   help="minimum severity that causes a non-zero exit "
                        "(default: error)")
    p.add_argument("--no-color", action="store_true", help="disable ANSI colors")
    p.add_argument("--version", action="version",
                   version=f"skillcheck {__version__}")
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    root = Path(args.path).resolve()
    if not root.exists():
        print(f"skillcheck: path not found: {root}", file=sys.stderr)
        return 2

    skills, findings = lint_path(root)

    if args.json:
        print(render_json(skills, findings, root))
    else:
        color = sys.stdout.isatty() and not args.no_color
        print(render_text(skills, findings, root, color=color))

    if not skills:
        print("skillcheck: no SKILL.md found", file=sys.stderr)
        return 2

    threshold = _THRESHOLD[args.fail_on]
    worst = max((f.severity for f in findings), default=Severity.INFO)
    if findings and worst >= threshold:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
