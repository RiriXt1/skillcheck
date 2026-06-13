"""skillcheck — a linter for Agent Skills (SKILL.md)."""

__version__ = "0.1.0"

from .core import Finding, Severity, SkillFile, lint_path

__all__ = ["Finding", "Severity", "SkillFile", "lint_path", "__version__"]
