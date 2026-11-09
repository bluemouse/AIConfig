#!/usr/bin/env python3
"""Mechanical lint for drafted commit messages (commit-message-writer skill).

Enforces the vocabulary half of the message-style contract that drafting
alone has repeatedly missed: no ephemeral planning/review ids, no run
narration, a Conventional Commits subject within 72 characters, and no
attribution footers. The semantic half (does the message state the why,
does it match the diff) remains the drafter's job.

Usage:
    python <SKILL_ROOT>/scripts/lint_message.py MESSAGE_FILE
    python <SKILL_ROOT>/scripts/lint_message.py -          # read from stdin

Exit codes:
    0 — message passes the lint
    1 — one or more violations (printed to stderr)
    2 — usage error

Harness twin: the dev-workflow harness ships the same rule set as an
enforcing phase gate at .ai/tools/dev-workflow/checks/message_checks.py.
Keep the two in sync.
"""

from __future__ import annotations

import re
import sys

SUBJECT_PREFIX_RE = re.compile(
    r"^(feat|fix|docs|style|refactor|perf|test|build|ci|chore)(\([a-z0-9_-]+\))?: "
)

SUBJECT_MAX_LEN = 72

# Banned in subject and body: ephemeral run-artifact vocabulary and
# narration. Field-tested against the 2026-11-09 two-day reword (14 real
# messages) plus their pre-reword originals.
_BANNED: tuple[tuple[re.Pattern[str], str], ...] = (
    # Run-artifact id grammar (harness task/finding/refinement ids and the
    # letter+digit id classes used by review runs).
    (re.compile(r"\b(?:cr|fdr|pg|df|sx|pr2?|rr|dfcr|lo)-\d"), "run-artifact id"),
    (re.compile(r"\bt-\d+[ab]?\b"), "test task id"),
    (re.compile(r"\bR\d{1,2}\b(?!\.)"), "refinement id"),
    (re.compile(r"\b[FDCGAE]\d\d\b"), "finding id"),
    (re.compile(r"\bB2\d\b"), "finding id"),
    (re.compile(r"\b[MDH]\d{1,2}\b(?!\.)"), "finding id"),
    (re.compile(r"\b(?:LOW|HIGH)\b"), "severity label"),
    # Run narration and planning-artifact references.
    (re.compile(r"[Ss]tage \d"), "stage narration"),
    (re.compile(r"round-\d"), "review-round narration"),
    (re.compile(r"\bledger(?:ed)?\b"), "run-ledger narration"),
    (re.compile(r"user[- ](?:decision|approved)"), "user-approval narration"),
    (re.compile(r"deep review"), "review narration"),
    (re.compile(r"review fix"), "review narration"),
    (re.compile(r"\bfindings?\b"), "review narration"),
    (re.compile(r"as planned|as discussed|per the (?:plan|review)"), "planning-artifact reference"),
)

_COAUTHORED_RE = re.compile(r"^Co-authored-by:", re.MULTILINE)
_SIGNED_OFF_RE = re.compile(r"^Signed-off-by:", re.MULTILINE)


def lint_message_text(text: str) -> list[str]:
    """Return human-readable violations for a commit message (pure function)."""
    violations: list[str] = []
    lines = text.strip().splitlines()
    if not lines:
        return ["empty message"]

    subject = lines[0]
    if not SUBJECT_PREFIX_RE.match(subject):
        violations.append(f"subject is not a Conventional Commits line: {subject!r}")
    if len(subject) > SUBJECT_MAX_LEN:
        violations.append(f"subject exceeds {SUBJECT_MAX_LEN} characters ({len(subject)}): {subject!r}")
    if subject.rstrip().endswith("."):
        violations.append(f"subject has a trailing period: {subject!r}")

    for pattern, label in _BANNED:
        match = pattern.search(text)
        if match:
            excerpt = text[max(0, match.start() - 20):match.end() + 20].replace("\n", " ")
            violations.append(f"banned {label}: ...{excerpt}...")

    if _COAUTHORED_RE.search(text):
        violations.append("attribution footer: Co-authored-by")
    if _SIGNED_OFF_RE.search(text):
        violations.append("attribution footer: Signed-off-by (warning-tier)")
    return violations


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    source = sys.argv[1]
    try:
        text = sys.stdin.read() if source == "-" else open(source, encoding="utf-8").read()
    except OSError as exc:
        print(f"ERROR: cannot read message: {exc}", file=sys.stderr)
        return 2

    violations = lint_message_text(text)
    if violations:
        print("COMMIT MESSAGE LINT FAILED:", file=sys.stderr)
        for violation in violations:
            print(f"  - {violation}", file=sys.stderr)
        return 1
    print("COMMIT MESSAGE LINT PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
