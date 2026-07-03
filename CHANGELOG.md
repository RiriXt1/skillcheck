# Changelog

All notable changes to `skillcheck` are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-06-09

### Added

- **Frontmatter validation** — checks every `SKILL.md` has a valid `name`
  (lowercase, hyphens/underscores, ≤64 chars) and a non-empty `description`
  (warns if >1024 chars).
- **Secret detection** — scans for AWS access keys (`AKIA...`), OpenAI tokens
  (`sk-...`), GitHub PATs (`ghp_...`), fine-grained PATs, Google API keys,
  Slack tokens, JWTs, PEM private keys, hex wallet keys, and generic
  `api_key = "..."` assignments.
- **Duplicate name detection** — flags skills that declare the same `name`,
  which causes router coin-flips.
- **Trigger collision detection** — measures keyword overlap (Jaccard
  similarity ≥0.6) between skill descriptions and warns when the router
  cannot disambiguate them.
- **Description quality** — warns on descriptions shorter than 20 chars and
  flags generic openings ("a skill that helps you...").
- **CLI** — `skillcheck <path>` with `--json`, `--fail-on`, `--no-color`, and
  `--version` flags. Exit codes: 0 (clean), 1 (findings at or above
  threshold), 2 (usage error).
- **CI workflow** — GitHub Actions running tests on Python 3.9, 3.11, and
  3.13.
- **Test suite** — 15 tests covering all rules with deliberately broken
  fixtures (anti-false-confidence pattern).
- **MIT license**.
