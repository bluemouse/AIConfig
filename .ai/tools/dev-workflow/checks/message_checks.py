"""Category 6: Commit-message checks.

Lint commit messages made during a phase against the commit-message
self-containment contract: no ephemeral planning/review ids, no run
narration, a Conventional Commits subject within 72 characters, and no
attribution footers. The rules mirror the commit-message-writer skill's
message-style contract (references/message-style-contract.md, "Self-contained
messages"): a commit message must be readable from the repository alone, and
finding/task/stage ids carry meaning only inside the run artifacts that
define them.

Baseline mechanism (same as mode checks): commits in baseline_head..HEAD were
made during this phase and are linted. In staged mode the per-stage commits
land during the implement phase and fix-loop commits during the code-review
phase, so those phases are linted too — not just the commit phase.

False positives follow the established repair: record the override with
justification in the manifest validation log, re-record the baseline
mid-phase (absorbing the commit), and re-run the checks.

Portable twin: the same rule set ships with the commit-message-writer skill
as scripts/lint_message.py for ad-hoc draft-time use. Keep the two in sync.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

from . import Finding
from . import mode_checks

# Phases whose commits are linted. Staged-mode per-stage commits (implement)
# and fix-loop commits (code-review) are the most common leak points.
LINT_PHASES = {"implement", "code-review", "commit"}

# Conventional Commits subject prefix.
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

# Attribution footers. Co-authored-by is always wrong here; Signed-off-by is
# usually a human DCO sign-off, so it is only a warning.
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


def _phase_commits(repo_root: Path, baseline_head: str) -> list[tuple[str, str]] | None:
    """Return (sha, message) pairs for commits in baseline_head..HEAD, or None on git failure."""
    try:
        result = subprocess.run(
            ["git", "log", "--format=%H%x00%B%x00", f"{baseline_head}..HEAD"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (subprocess.SubprocessError, FileNotFoundError):
        return None
    if result.returncode != 0:
        return None
    commits: list[tuple[str, str]] = []
    parts = result.stdout.split("\x00")
    # parts alternates sha, message, sha, message, ... with a trailing empty part.
    for i in range(0, len(parts) - 1, 2):
        sha = parts[i].strip()
        message = parts[i + 1] if i + 1 < len(parts) else ""
        if sha:
            commits.append((sha, message))
    return commits


def check_commit_messages(run_dir: Path, phase: str, repo_root: Path | None = None) -> list[Finding]:
    """Lint commits made during this phase against the message contract.

    Only fires when HEAD advanced beyond the phase-start baseline, so
    dispositioned commits absorbed by a mid-phase re-baseline are not
    re-flagged (same repair flow as the other mode-enforcement checks).
    """
    if phase not in LINT_PHASES:
        return []
    if repo_root is None:
        return []

    baseline = mode_checks._read_baseline(run_dir)
    if baseline is None:
        return []

    current_head = mode_checks._get_current_head(repo_root)
    if current_head is None:
        return [Finding(
            severity="warning",
            check="commit_message",
            message="Could not run git rev-parse to verify commit messages",
        )]
    if current_head == baseline["head"]:
        return []

    commits = _phase_commits(repo_root, baseline["head"])
    if commits is None:
        return [Finding(
            severity="warning",
            check="commit_message",
            message=(
                "Could not enumerate commits since baseline "
                f"{baseline['head'][:8]} to lint messages"
            ),
        )]

    findings: list[Finding] = []
    for sha, message in commits:
        for violation in lint_message_text(message):
            findings.append(Finding(
                severity="error",
                check="commit_message",
                message=f"commit {sha[:8]}: {violation}",
            ))
    return findings
