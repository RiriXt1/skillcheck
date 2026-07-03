# skillcheck

[![CI](https://github.com/RiriXt1/skillcheck/actions/workflows/ci.yml/badge.svg)](https://github.com/RiriXt1/skillcheck/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](pyproject.toml)
[![Tests](https://img.shields.io/badge/tests-15%20passing-brightgreen.svg)](tests/)

A linter for [Agent Skills](https://github.com/anthropics/skills) — the `SKILL.md` files that teach Claude, Codex, Cursor, and other agents how to do things.

The skill format went open in late 2025. People started shipping dozens, then hundreds of them. The problems show up fast:

- A skill with no `description` never gets picked.
- Two skills with near-identical descriptions make the agent flip a coin.
- A skill someone copy-pasted an API key into gets committed to a public repo.

None of that throws an error. It just quietly makes your agent worse. `skillcheck` catches it before it ships.

## What it checks

| Rule | Severity | Description |
|------|----------|-------------|
| `frontmatter` | Error | Missing `name` or `description`, malformed YAML |
| `frontmatter.name` | Warn | Name not lowercase, too long, invalid chars |
| `frontmatter.description` | Warn | Description >1024 chars (costs tokens on every boot) |
| `duplicate-name` | Error | Two skills claiming the same `name` |
| `secret` | Error | AWS keys, OpenAI tokens, GitHub PATs, JWTs, private keys, hex wallet keys, generic `api_key = "..."` |
| `description.short` | Warn | Description <20 chars — too short to route on |
| `description.generic` | Info | Description starts with filler ("a skill that...") |
| `trigger-collision` | Warn | Two descriptions share ≥60% of keywords — router can't disambiguate |

## Install

```bash
pip install skillcheck
```

## Usage

```bash
# scan a directory of skills (recursively finds every SKILL.md)
skillcheck ./skills

# check one skill
skillcheck ./skills/pdf/SKILL.md

# machine-readable output for CI
skillcheck ./skills --json

# only fail on hard errors, let warnings through
skillcheck ./skills --fail-on error
```

Exit codes:

| Code | Meaning |
|------|---------|
| `0` | Clean — no findings at or above threshold |
| `1` | Findings detected at or above `--fail-on` level |
| `2` | Usage error (no skills found, bad path) |

### In CI

```yaml
- run: pip install skillcheck
- run: skillcheck ./skills --fail-on error
```

### Example

```
  skills/pdf/SKILL.md
    ✗ frontmatter.description: missing required field 'description'

  skills/pdf-tools/SKILL.md
    ! trigger-collision: 'pdf' and 'pdf-tools' share 71% of trigger keywords
      (merge, pdf, pages, split, extract); router may tie between them

  scanned 14 skill(s)
  1 error(s), 1 warning(s), 0 info
```

## What it is not

It's a linter, not a sandbox. It reads files and matches patterns — it doesn't execute skill scripts or judge whether the *instructions* inside a skill are any good. The secret scan uses well-known token shapes; a homemade secret format won't trip it. Treat a clean run as "no obvious structural problems," not "audited and safe."

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on adding rules, writing tests, and submitting PRs.

## Changelog

See [CHANGELOG.md](CHANGELOG.md).

## Security

See [SECURITY.md](SECURITY.md) for vulnerability reporting and disclosure policy.

## License

[MIT](LICENSE)
