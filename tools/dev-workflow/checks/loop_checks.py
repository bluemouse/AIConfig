"""Category 3: Loop contract checks.

Verify that checkers emitted valid verdicts, included root-cause-phase on
findings, and that loop round counts respect caps.
"""

from __future__ import annotations

import re
from pathlib import Path

from . import Finding
from . import artifact_checks
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

# ar-002/ar-013: root-cause-phase vocabulary per phase. Keep in lockstep with
# loop-contracts.md "Root cause field" rows and the checker skill/agent bodies.
ROOT_CAUSE_VALUES: dict[str, set[str]] = {
    "research": {"local", "research", "clarify", "plan", "implement", "code-review"},
    "plan": {"local", "research", "clarify", "plan", "implement", "code-review"},
    "implement": {"local", "research", "clarify", "plan", "implement", "code-review"},
    "code-review": {"local", "research", "clarify", "plan", "implement", "code-review"},
}

# Final doer artifact for each completed loop. The code-review loop starts with
# a review, but a completed loop must end with the reviewer consuming the fix report.
PHASE_DOER: dict[str, str] = {
    "research": "10-research-report.md",
    "plan": "20-implementation-plan.md",
    "implement": "30-implementation-report.md",
    "code-review": "41-fix-report.md",
}


def _resolve_checker_path(run_dir: Path, phase: str) -> Path | None:
    """Resolve the checker artifact path, including stage-indexed variants.

    In staged mode, 31-stage1-implementation-audit.md satisfies the
    31-implementation-audit.md requirement (and similarly for 40-stageN-*).
    Falls back to the exact filename in linear mode.
    """
    checker_file = PHASE_CHECKER.get(phase)
    if not checker_file:
        return None
    staged = artifact_checks._is_staged_mode(run_dir)
    return artifact_checks._resolve_artifact_path(run_dir, checker_file, phase, staged)


def _resolve_doer_path(run_dir: Path, phase: str) -> Path | None:
    """Resolve the doer artifact path, including stage-indexed variants."""
    doer_file = PHASE_DOER.get(phase)
    if not doer_file:
        return None
    staged = artifact_checks._is_staged_mode(run_dir)
    return artifact_checks._resolve_artifact_path(run_dir, doer_file, phase, staged)

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
    path = _resolve_checker_path(run_dir, phase)
    if path is None:
        return []  # Already reported by artifact_checks

    text = path.read_text(encoding="utf-8")
    # Look up valid verdicts by the actual filename (supports stage-indexed
    # globs like 31-stage*-implementation-audit.md via lookup_verdicts_for_filename).
    valid_verdicts = lookup_verdicts_for_filename(path.name, CHECKER_VERDICTS)
    # Fall back to the canonical filename's verdicts if the actual filename
    # has no entry (e.g. stage-indexed variants not yet registered).
    if not valid_verdicts:
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
    path = _resolve_checker_path(run_dir, phase)
    if path is None:
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

    # ar-013: require the field in each finding's block and validate its
    # value against the phase's allowed vocabulary (ROOT_CAUSE_VALUES).
    #
    # A finding *definition* is the id at the start of a heading or list
    # item — the position where a checker authors a finding (detail sections
    # in the report templates use `#### rr-001: ...`). Summary-table rows
    # and prior-round disposition rows mention ids without defining
    # findings, so they are not presence-checked. A definition's block runs
    # to the next finding-id occurrence of any form (heading, list item, or
    # table row), so a missing field in one finding cannot be masked by a
    # later finding's field (the ar-013 round-3 false negative).
    allowed = ROOT_CAUSE_VALUES.get(phase, set())
    # A finding *definition* is the id at the start of a heading or a
    # header-shaped list item (id followed by `:` or an em dash — the detail
    # sections' `- rr-001: ...` / `#### rr-001: ...` conventions). A bare
    # line-initial reference bullet ("- consider cr-001 first" in Next
    # actions) is a mention, not a definition, so it is not
    # presence-checked (cr-013).
    definition_pattern = re.compile(
        r"^#{2,6}\s+(?:finding\s+)?[*`]*((?:rr|pr|ia|cr)-\d{3})\b"
        r"|^[-*]\s+[*`]*((?:rr|pr|ia|cr)-\d{3})\s*[:—-]\s",
        re.IGNORECASE | re.MULTILINE,
    )
    boundary_pattern = re.compile(
        r"^#{2,6}\s+(?:finding\s+)?[*`]*(?:rr|pr|ia|cr)-\d{3}\b"
        r"|^[-*]\s+[*`]*(?:rr|pr|ia|cr)-\d{3}\b"
        r"|^\|[^|\n]*\b(?:rr|pr|ia|cr)-\d{3}\b",
        re.IGNORECASE | re.MULTILINE,
    )
    boundary_starts = [m.start() for m in boundary_pattern.finditer(text)]
    for definition in definition_pattern.finditer(text):
        finding_id = definition.group(1) or definition.group(2)
        block_end = next(
            (start for start in boundary_starts if start > definition.start()),
            len(text),
        )
        block = text[definition.start():block_end]
        if "root-cause-phase" not in block.lower():
            findings.append(Finding(
                severity="error",
                check="loop_contract",
                message=(
                    f"Finding {finding_id} in {checker_file} has no "
                    f"'root-cause-phase' field in its block"
                ),
            ))

    # Value vocabulary applies to every field occurrence in the artifact —
    # definition blocks and summary-table root-cause columns alike — so a
    # value outside the phase's vocabulary is flagged wherever it appears.
    value_pattern = re.compile(
        r"root-cause-phase\s*[:`]\s*`?(\w[\w-]*)", re.IGNORECASE
    )
    for value_match in value_pattern.finditer(text):
        value = value_match.group(1).lower()
        if allowed and value not in allowed:
            findings.append(Finding(
                severity="error",
                check="loop_contract",
                message=(
                    f"root-cause-phase '{value_match.group(1)}' in {checker_file} "
                    f"is not in the phase's vocabulary {sorted(allowed)}"
                ),
            ))
    # Summary-table occurrences: the label lives in the header cell, so the
    # labeled-field pattern misses them. Locate the column via the header
    # row, then scan only that table's contiguous body rows — the scan stops
    # at the first non-table line, so later unrelated tables are never
    # validated against this column, and the markdown separator row
    # (all cells `-`/`:`/space) is skipped (cr-008).
    if allowed:
        table_line_pattern = re.compile(r"^\|[^\n]*\|[^\n]*$", re.MULTILINE)
        for header_match in table_line_pattern.finditer(text):
            line = header_match.group(0)
            cells = [c.strip().strip("`").lower() for c in line.split("|")[1:-1]]
            if "root-cause-phase" not in cells:
                continue
            value_index = cells.index("root-cause-phase")
            body = text[header_match.end():]
            row_matches = list(table_line_pattern.finditer(body))
            for row_idx, row_match in enumerate(row_matches):
                prev_end = (
                    row_matches[row_idx - 1].end()
                    if row_idx > 0
                    else 0
                )
                # Contiguous table rows are separated by exactly one newline
                # (cr-014). Markdown ends a table at a blank line — any gap
                # other than a single "\n" (blank line, prose, heading) means
                # the table ended and the scan must stop, or the next table's
                # cells would be validated against this column index.
                if body[prev_end:row_match.start()] != "\n":
                    break
                row_line = row_match.group(0)
                row_cells = [c.strip() for c in row_line.split("|")[1:-1]]
                if all(re.fullmatch(r"[-: ]*", c) for c in row_cells):
                    continue  # markdown separator row
                if len(row_cells) <= value_index:
                    continue
                value = row_cells[value_index].strip("`").lower()
                # Placeholder tolerance (cr-015): templates list the allowed
                # values as a slash-separated placeholder (e.g.
                # `local/research/clarify/plan/implement/code-review`), and a
                # checker may copy the row verbatim — the verdict extractor
                # tolerates exactly this via strip_placeholder_options. Real
                # values are single hyphenated words; skip cells that carry
                # slash-separated option lists rather than flagging them.
                if "/" in value:
                    continue
                if value and value not in allowed:
                    findings.append(Finding(
                        severity="error",
                        check="loop_contract",
                        message=(
                            f"root-cause-phase '{row_cells[value_index].strip().strip('`')}' "
                            f"in {checker_file} is not in the phase's vocabulary "
                            f"{sorted(allowed)}"
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
    prefixes = artifact_checks.allowed_prefixes_for_phase(
        run_dir, phase, PHASE_ARTIFACT_PREFIXES.get(phase, set())
    )
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


def _stage_index_of(path: Path) -> int | None:
    """Extract the stage number from a stage-indexed artifact filename.

    Returns the 1-indexed stage number for names like ``31-stage2-implementation-audit.md``,
    or None for linear-mode names (no ``-stageN-`` segment).
    """
    match = re.match(r"^\d{2}-stage(\d+)-", path.name)
    if match:
        return int(match.group(1))
    return None


def check_doer_precedes_checker(run_dir: Path, phase: str) -> list[Finding]:
    """Check that the checker artifact was written after its doer input.

    Validation runs on an accept verdict, and every accept verdict is written
    by the checker — so at validation time the checker artifact must be the
    newest file of the pair. This holds for the code-review phase too: the
    loop's *procedure* starts with the reviewer (round 1) but a completed loop
    ends with the reviewer consuming the fix report, so the final re-review in
    ``40-code-review.md`` is still the newest write.

    In staged mode, both artifacts must come from the same stage: comparing a
    stage-1 review against a stage-2 fix report is meaningless because later
    stages naturally write later files. When the resolved pair carries
    different stage indices, the check is skipped (the pairing is ambiguous,
    not provably wrong).
    """
    checker_file = PHASE_CHECKER.get(phase)
    doer_file = PHASE_DOER.get(phase)
    if not checker_file or not doer_file:
        return []

    checker_path = _resolve_checker_path(run_dir, phase)
    doer_path = _resolve_doer_path(run_dir, phase)
    if checker_path is None or doer_path is None:
        return []  # Artifact structure checks report the missing file.

    # Staged mode: only compare artifacts from the same stage.
    checker_stage = _stage_index_of(checker_path)
    doer_stage = _stage_index_of(doer_path)
    if checker_stage != doer_stage:
        return []  # Cross-stage pairing is ambiguous; skip rather than guess.

    # All phases, including code-review: the checker's accept verdict is the
    # newest write at validation time.
    if doer_path.stat().st_mtime_ns > checker_path.stat().st_mtime_ns:
        return [Finding(
            severity="error",
            check="loop_contract",
            message=(
                f"Checker artifact {checker_path.name} predates its doer "
                f"artifact {doer_path.name}"
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
