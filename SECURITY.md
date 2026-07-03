# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | Yes       |

## Reporting a Vulnerability

If you discover a security vulnerability in `skillcheck`, please report it
responsibly:

1. **Do not open a public issue.**
2. Email the maintainer at **ririxt1@users.noreply.github.com** with a
   description of the vulnerability, steps to reproduce, and potential impact.
3. You will receive an acknowledgment within 72 hours.
4. A fix or mitigation will be prioritized based on severity.

## Scope

`skillcheck` is a static analysis tool. It reads files and matches patterns —
it does not execute code. Vulnerabilities in `skillcheck` itself (e.g., regex
DoS, path traversal during discovery, unsafe YAML parsing) are in scope.

Vulnerabilities in the skill files that `skillcheck` scans are **out of scope**
— the tool reports issues, it does not fix them.

## Secret Detection Limitations

The secret scanner uses well-known token shapes (AWS, OpenAI, GitHub PAT,
JWT, PEM keys, hex wallet keys, generic assignments). It will not catch:

- Custom or non-standard secret formats
- Secrets split across multiple lines
- Secrets in binary or encoded files

A clean scan means "no obvious structural problems," not "audited and safe."

## Disclosure Timeline

- **Day 0**: Report received and acknowledged.
- **Day 1-3**: Triage and severity assessment.
- **Day 3-14**: Fix developed and tested privately.
- **Day 14**: Public advisory + patched release (if applicable).

We request a 90-day embargo before public disclosure. Coordinated disclosure
is preferred.
