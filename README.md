# skillcheck

A linter for [Agent Skills](https://github.com/anthropics/skills) — the `SKILL.md` files that teach Claude, Codex, Cursor, and other agents how to do things.

The skill format went open in late 2025 and people started shipping dozens, then hundreds of them. The problem shows up fast: a skill with no `description` never gets picked. Two skills with near-identical descriptions make the agent flip a coin. A skill someone copy-pasted an API key into gets committed to a public repo. None of that throws an error — it just quietly makes your agent worse.

`skillcheck` catches those before they ship.

## What it checks

- **Frontmatter** — every `SKILL.md` needs a valid `name` and a `description`. Missing or malformed ones are errors; oversized descriptions are warnings (you pay for them on every agent boot).
- **Leaked secrets** — AWS keys, OpenAI `sk-` tokens, GitHub PATs, JWTs, private keys, hex wallet keys, and the classic `API_KEY = "..."` assignment. A skill file is the last place you want one.
- **Duplicate names** — two skills claiming the same `name` is a coin flip for the router.
- **Trigger collisions** — if two descriptions share most of their keywords, the agent can't tell them apart. This is the bug that makes routing feel flaky. skillcheck measures the keyword overlap and warns you.
- **Description quality** — too short to route on, or starts with filler like "a skill that helps you...".

## Install

```bash
pip install skillcheck
```

## Use

```bash
# scan a directory of skills (recursively finds every SKILL.md)
skillcheck ./skills

# check one skill
skillcheck ./skills/pdf/SKILL.md

# machine-readable output for CI
skillcheck ./skills --json

# only fail the build on hard errors, let warnings through
skillcheck ./skills --fail-on error
```

Exit code is `0` when clean, `1` when something at or above `--fail-on` is found, `2` for usage problems (no skills found, bad path). That's the contract CI cares about.

### In CI

```yaml
- run: pip install skillcheck
- run: skillcheck ./skills --fail-on error
```

## Example

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

## Why it exists

It started as a pile of one-off scripts for keeping one agent's skill library tidy — a frontmatter check here, a router tie-detector there, a secret tripwire bolted on after a near-miss. At some point the scripts were more useful than the cleanup that prompted them, so they got pulled into one tool. If you're maintaining more than a handful of skills, you'll hit the same walls.

## Contributing

Rules live in `src/skillcheck/rules.py` and each one is a small, independent function with a test in `tests/`. Adding a check is: write the function, add it to `ALL_RULES`, write a fixture that's deliberately broken so you prove it fires. PRs and issues welcome.

## License

MIT
