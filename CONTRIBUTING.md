# Contributing to skillcheck

Thanks for your interest in improving `skillcheck`. This document describes
how to contribute bug reports, feature requests, and code.

## Before You Start

- Check existing [issues](https://github.com/RiriXt1/skillcheck/issues) to
  avoid duplicates.
- For major changes, open an issue first to discuss what you want to change.
- Small fixes (typos, docs, minor bugs) can go straight to a PR.

## Adding a New Rule

Rules live in [`src/skillcheck/rules.py`](src/skillcheck/rules.py). Each rule
is a small, independent function with the signature:

```python
def rule_something(skills: list[SkillFile], root: Path) -> list[Finding]:
    ...
```

Steps:

1. Write the rule function. Keep it focused — one rule, one concern.
2. Add it to the `ALL_RULES` list at the bottom of the file.
3. Write a test in `tests/` that deliberately triggers the rule (the
   "anti-false-confidence" pattern: if your fixture is clean, the test is
   meaningless).
4. Add the test fixture to `tests/`.
5. Run `PYTHONPATH=src pytest tests/ -v` and confirm everything passes.
6. If the rule adds a new severity, update `report.py` icons and colors.

## Adding a Secret Pattern

Secret patterns are in `_SECRET_PATTERNS` inside `rules.py`. Add a tuple of
`(name, compiled_regex)`. Test it with a deliberately leaked fixture.

## Code Style

- Python 3.9+ (the minimum supported version). No 3.10+ syntax features
  (e.g., `match` statements) unless behind `from __future__` imports.
- `from __future__ import annotations` is used throughout — keep it.
- Type hints are required. The codebase is fully typed.
- Functions stay small and independent. A rule should never depend on another
  rule's output.

## Testing

```bash
# install in editable mode
pip install -e .

# run all tests
PYTHONPATH=src pytest tests/ -v

# run a specific test file
PYTHONPATH=src pytest tests/test_rules.py -v

# dogfood: lint your own skills
skillcheck ~/.hermes/skills --fail-on error
```

Each test uses `pytest`'s `tmp_path` fixture — no shared state between tests.
Tests that write fixtures must use `_write_skill()` or create files manually
in `tmp_path`.

## Pull Request Checklist

- [ ] Tests pass locally (`PYTHONPATH=src pytest tests/ -v`)
- [ ] New rules have at least one test that proves they fire
- [ ] No secret values committed (run `skillcheck .` on your own repo)
- [ ] Commit messages follow conventional commits (`feat:`, `fix:`, `docs:`,
      `test:`, `refactor:`, `chore:`)
- [ ] If adding a dependency, it is justified and pinned in `pyproject.toml`

## Reporting Bugs

Open an [issue](https://github.com/RiriXt1/skillcheck/issues) with:

1. `skillcheck` version (`skillcheck --version`)
2. Python version (`python --version`)
3. The SKILL.md content that triggers the bug (or a minimal reproduction)
4. Expected behavior vs. actual output

## License

By contributing, you agree that your contributions are licensed under the MIT
license (see [LICENSE](LICENSE)).
