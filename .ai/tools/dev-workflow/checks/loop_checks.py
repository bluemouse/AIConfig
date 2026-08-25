"""Category 3: Loop contract checks.

Verify that checkers emitted valid verdicts, included root-cause-phase on
findings, and that loop round counts respect caps.
"""

from __future__ import annotations

import re
from pathlib import Path

from . import Finding
from .verdicts import CHECKER_VERDICTS, extract_verdict, lookup_verdicts_for_filename, match_verdict

# Loop round caps per phase. Clarify has no cap (interactive, no fixed round limit).
LOOP_CAPS: dict[str, int] = {
    "research": 5,
    "plan": 3,
    "implement": 3,
    "code-review": 5,
}

# Checker artifact per phase. Clarify has no checker.
PHASE_CHECKER: dict[str, str] = {
    "research": "11-research-review.md",
    "plan": "21-plan-review.md",
    "implement": "31-implementation-audit.md",
    "code-review": "40-code-review.md",
}

# Final doer artifact for each completed loop. The code-review loop starts with
# a review, but a completed loop must end with the reviewer consuming the fix report.
PHASE_DOER: dict[str, str] = {
    "research": "10-research-report.md",
    "plan": "20-implementation-plan.md",
    "implement": "30-implementation-report.md",
    "code-review": "41-fix-report.md",
}

PHASE_ARTIFACT_PREFIXES: dict[str, set[str]] = {
    "research": {"10", "11", "12", "13", "14", "15"},
    "plan": {"20", "21", "22", "23"},
    "implement": {"30", "31", "32", "33"},
    "code-review": {"40", "41", "42", "43"},
}


def check_verdict_valid(run_dir: Path, phase: str) -> list[Finding]:
    """Check that the checker's verdict is one of the allowed values."""
    findings: list[Finding] = []
    checker_file = PHASE_CHECKER.get(phase)
    if not checker_file:
        return []
    path = run_dir / checker_file
    if not path.exists():
        return []  # Already reported by artifact_checks

    text = path.read_text(encoding="utf-8")
    valid_verdicts = lookup_verdicts_for_filename(checker_file, CHECKER_VERDICTS)

    found_verdict = extract_verdict(text)

    if found_verdict is None:
        findings.append(Finding(
            severity="error",
            check="loop_contract",
            message=f"No verdict found in {checker_file}",
        ))
    elif valid_verdicts:
        # Use exact matching via the verdicts module.
        matched = match_verdict(found_verdict, valid_verdicts)
        if not matched:
            findings.append(Finding(
                severity="error",
                check="loop_contract",
                message=(
                    f"Invalid verdict in {checker_file}: '{found_verdict}'. "
                    f"Expected one of: {', '.join(sorted(valid_verdicts))}"
                ),
            ))
    return findings


def check_root_cause_phase_present(run_dir: Path, phase: str) -> list[Finding]:
    """Check that findings in the checker report include root-cause-phase field."""
    findings: list[Finding] = []
    checker_file = PHASE_CHECKER.get(phase)
    if not checker_file:
        return []
    path = run_dir / checker_file
    if not path.exists():
        return []

    text = path.read_text(encoding="utf-8")

    # Look for finding ids (rr-NNN, pr-NNN, ia-NNN, cr-NNN)
    finding_id_pattern = re.compile(
        r"(?:rr|pr|ia|cr)-\d{3}", re.IGNORECASE
    )
    finding_ids = finding_id_pattern.findall(text)

    if not finding_ids:
        # No findings at all — this is fine if the verdict is positive
        return []

    # Check if root-cause-phase appears in the text
    if "root-cause-phase" not in text.lower():
        findings.append(Finding(
            severity="error",
            check="loop_contract",
            message=(
                f"Findings present in {checker_file} but no "
                f"'root-cause-phase' field found"
            ),
        ))
    return findings


def check_loop_cap_respected(run_dir: Path, phase: str) -> list[Finding]:
    """Check that the number of round artifacts doesn't exceed the loop cap."""
    findings: list[Finding] = []
    cap = LOOP_CAPS.get(phase)
    if cap is None:
        return []

    # Round artifacts are named with a -rN suffix. The highest suffix within the
    # current phase's prefix range is the number of iterations.
    rounds = 1
    prefixes = PHASE_ARTIFACT_PREFIXES.get(phase, set())
    for path in run_dir.iterdir():
        if not path.is_file() or not path.name.endswith(".md"):
            continue
        if path.name[:2] not in prefixes:
            continue
        match = re.search(r"-r(\d+)\.md$", path.name, re.IGNORECASE)
        if match:
            rounds = max(rounds, int(match.group(1)))
    if rounds > cap:
        findings.append(Finding(
            severity="error",
            check="loop_contract",
            message=(
                f"Loop cap exceeded for {phase}: {rounds} rounds > cap of {cap}"
            ),
        ))
    return findings


def check_doer_precedes_checker(run_dir: Path, phase: str) -> list[Finding]:
    """Check that the final checker artifact was written after its doer input."""
    checker_file = PHASE_CHECKER.get(phase)
    doer_file = PHASE_DOER.get(phase)
    if not checker_file or not doer_file:
        return []

    checker_path = run_dir / checker_file
    doer_path = run_dir / doer_file
    if not checker_path.exists() or not doer_path.exists():
        return []  # Artifact structure checks report the missing file.

    if doer_path.stat().st_mtime_ns > checker_path.stat().st_mtime_ns:
        return [Finding(
            severity="error",
            check="loop_contract",
            message=(
                f"Checker artifact {checker_file} predates its doer artifact "
                f"{doer_file}"
            ),
        )]
    return []


def run_all(run_dir: Path, phase: str) -> list[Finding]:
    """Run all loop contract checks for a phase."""
    findings: list[Finding] = []
    # Clarify phase has no checker, no verdict, no round cap, no root-cause-phase.
    if phase == "clarify":
        return findings
    findings.extend(check_verdict_valid(run_dir, phase))
    findings.extend(check_root_cause_phase_present(run_dir, phase))
    findings.extend(check_loop_cap_respected(run_dir, phase))
    findings.extend(check_doer_precedes_checker(run_dir, phase))
    return findings
