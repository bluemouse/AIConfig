"""Category 1: Artifact structure checks.

Verify that expected artifacts exist at expected paths and contain required sections.
"""

from __future__ import annotations

import re
from pathlib import Path

from . import Finding

# Expected artifacts per phase. Keyed by phase name.
# Each entry: (filename, required_sections) where required_sections is a list
# of markdown headings that must appear in the file.
PHASE_ARTIFACTS: dict[str, list[tuple[str, list[str]]]] = {
    "clarify": [
        ("02-requirement-ledger.md", ["# Requirement Ledger", "## Outcome", "## Scope", "## Acceptance criteria", "## Assumptions"]),
    ],
    "research": [
        ("10-research-report.md", ["# Research Report", "## Problem statement"]),
        ("11-research-review.md", ["## Verdict"]),
    ],
    "plan": [
        ("20-implementation-plan.md", ["# Implementation Plan", "## Planning status"]),
        ("21-plan-review.md", ["## Verdict"]),
    ],
    "implement": [
        ("30-implementation-report.md", ["# Implementation Report"]),
        ("31-implementation-audit.md", ["## Verdict"]),
    ],
    "code-review": [
        ("40-code-review.md", ["# Code Review Report"]),
        ("41-fix-report.md", ["# Fix Report", "## Summary"]),
    ],
    "commit": [
        ("50-commit.md", ["# Commit Record"]),
    ],
}


def _heading_variants(heading: str) -> list[str]:
    """Return the heading plus a numbered variant (e.g. ``## 3. Problem statement``).

    Templates number some sections (``## 3. Problem statement``) while the
    required-section lists use unnumbered forms. Both satisfy the requirement;
    a numbered heading is the same section with an index prefix.
    """
    import re

    match = re.match(r"^(#{1,6})\s+(.+)$", heading)
    if not match:
        return [heading]
    hashes, title = match.groups()
    return [heading, f"{hashes} N. {title}"]


def _section_present(text: str, section: str) -> bool:
    """Check that a required section heading is present, tolerating numbering.

    Matches the exact unnumbered form (``## Problem statement``) or a
    numbered form (``## 3. Problem statement``) of the same heading.
    """
    for variant in _heading_variants(section):
        if variant in text:
            return True
    # Numbered variant: any digits between the hashes and the title.
    match = re.match(r"^(#{1,6})\s+(.+)$", section)
    if match:
        hashes, title = match.groups()
        if re.search(
            rf"^{re.escape(hashes)}\s+\d+\.\s+{re.escape(title)}\s*$",
            text,
            re.MULTILINE,
        ):
            return True
    return False

# Regex to extract the stage number from a stage-indexed filename.
# Matches patterns like 30-stage1-implementation-report.md, 31-stage2-implementation-audit.md, etc.
_STAGE_INDEX_RE = re.compile(r"^(\d{2})-stage(\d+)-(.+\.md)$")

# Staged-mode "final" artifact aliases. In staged mode, the final deep review
# and final fix report use the ``-final-`` infix instead of ``-stageN-``. These
# satisfy the canonical code-review artifact requirements in staged mode, so
# ``_resolve_artifact_path`` maps them here. See SKILL.md "Final deep review".
_FINAL_ARTIFACT_ALIASES: dict[str, str] = {
    "40-code-review.md": "40-final-deep-review.md",
    "41-fix-report.md": "41-final-fix-report.md",
}


def _is_staged_mode(run_dir: Path) -> bool:
    """Check whether the run is in staged mode by reading the manifest.

    Returns True if the manifest has `Run mode: staged`, False otherwise
    (including when the manifest is missing or the field is absent).
    Uses regex to match the exact field value, not a fragile substring match.
    """
    manifest_path = run_dir / "00-run-manifest.md"
    if not manifest_path.exists():
        return False
    text = manifest_path.read_text(encoding="utf-8")
    match = re.search(r"Run mode:\s*(\S+)", text)
    if match:
        return match.group(1) == "staged"
    return False


def _resolve_artifact_path(
    run_dir: Path, filename: str, phase: str, staged_mode: bool
) -> Path | None:
    """Resolve the on-disk path for an expected artifact.

    Returns the exact filename path if it exists, a stage-indexed variant
    in staged mode, or None if no matching artifact is present.

    The stage-indexed lookup is cross-phase: a stage-indexed variant of
    ``30-implementation-report.md`` (e.g. ``30-stage1-implementation-report.md``)
    satisfies the requirement regardless of which phase is asking, because the
    artifact was produced by the implement phase but is consumed by code-review.

    In staged mode, the final deep review (``40-final-deep-review.md``) and
    final fix report (``41-final-fix-report.md``) also satisfy the canonical
    ``40-code-review.md`` / ``41-fix-report.md`` requirements — see
    ``_FINAL_ARTIFACT_ALIASES``.
    """
    path = run_dir / filename
    if path.exists():
        return path
    if staged_mode:
        # Staged-mode "final" aliases (40-final-deep-review.md, 41-final-fix-report.md).
        alias = _FINAL_ARTIFACT_ALIASES.get(filename)
        if alias is not None:
            alias_path = run_dir / alias
            if alias_path.exists():
                return alias_path
        stage_path = _find_stage_indexed_artifact(run_dir, filename, phase)
        if stage_path is not None:
            return stage_path
    return None


def _code_review_has_findings(run_dir: Path, staged_mode: bool) -> bool:
    """Determine whether the code-review phase produced findings requiring a fix report.

    The fix report (41-fix-report.md) is required only when a review verdict is
    `needs revision` — the revise verdict that sends findings to
    code-review-resolver. Accept verdicts (`ready to commit`, `ready with
    notes`) exit the loop forward without a resolver pass, even when minor
    findings with cr-NNN ids are present, so no fix report is expected.
    A missing or unreadable verdict is reported separately by
    check_verdict_valid; it does not require a fix report here.
    In staged mode, any stage's code review or the final deep review counts.
    """
    from .verdicts import extract_verdict, match_verdict, REVISE_VERDICTS

    # Candidate review artifacts to inspect. In staged mode, also gather all
    # per-stage reviews (40-stageN-code-review.md) and the final deep review
    # explicitly, so findings detection does not depend on cross-phase
    # resolution happening to route 40-code-review.md to a stage variant.
    review_paths: list[Path] = []
    canonical = run_dir / "40-code-review.md"
    if canonical.exists():
        review_paths.append(canonical)
    if staged_mode:
        final_path = run_dir / "40-final-deep-review.md"
        if final_path.exists():
            review_paths.append(final_path)
        for path in run_dir.iterdir():
            if not path.is_file() or not path.name.endswith(".md"):
                continue
            # Per-stage reviews: 40-stageN-code-review.md
            if _STAGE_INDEX_RE.match(path.name) and path.name.startswith("40-"):
                if path not in review_paths:
                    review_paths.append(path)

    # Revise verdicts that require a fix report, across code-review artifacts.
    revise_verdicts = REVISE_VERDICTS.get("40-code-review.md", set())

    for path in review_paths:
        text = path.read_text(encoding="utf-8")
        verdict = extract_verdict(text)
        if verdict is not None and match_verdict(verdict, revise_verdicts):
            return True
    return False


def _required_artifacts(run_dir: Path, phase: str, staged_mode: bool) -> list[tuple[str, list[str]]]:
    """Return the artifacts required for a phase in this run.

    Most phases require all artifacts in PHASE_ARTIFACTS. The code-review
    phase conditionally requires the fix report (41-fix-report.md) only when
    the review produced findings or a `needs revision` verdict.
    """
    artifacts = list(PHASE_ARTIFACTS.get(phase, []))
    if phase == "code-review" and not _code_review_has_findings(run_dir, staged_mode):
        artifacts = [
            (filename, sections)
            for filename, sections in artifacts
            if not filename.startswith("41-")
        ]
    return artifacts


def _find_stage_indexed_artifact(
    run_dir: Path, expected_filename: str, phase: str
) -> Path | None:
    """Find a stage-indexed variant of an expected artifact.

    In staged mode, 30-stage1-implementation-report.md satisfies the
    30-implementation-report.md requirement. This function searches the run
    directory for a stage-indexed file matching the expected filename's
    prefix and suffix.

    The lookup is cross-phase: the ``phase`` argument is accepted for API
    compatibility but does not restrict the search, because stage-indexed
    artifacts are produced by one phase and consumed by another (e.g. the
    implement phase produces 30-stageN-* which the code-review phase consumes).

    Returns the path to the stage-indexed file if found, None otherwise.
    """
    # Extract the prefix (e.g., "30") and the suffix (e.g., "implementation-report.md")
    # from the expected filename (e.g., "30-implementation-report.md").
    if len(expected_filename) < 3 or expected_filename[2] != "-":
        return None
    prefix = expected_filename[:2]
    suffix = expected_filename[3:]  # e.g., "implementation-report.md"

    # Search for a file matching {prefix}-stage{N}-{suffix}
    for path in run_dir.iterdir():
        if not path.is_file() or not path.name.endswith(".md"):
            continue
        match = _STAGE_INDEX_RE.match(path.name)
        if match:
            file_prefix = match.group(1)
            file_suffix = match.group(3)
            if file_prefix == prefix and file_suffix == suffix:
                return path

    return None


def check_artifacts_exist(run_dir: Path, phase: str) -> list[Finding]:
    """Check that all expected artifacts for a phase exist.

    In staged mode (manifest has `Run mode: staged`), stage-indexed variants
    (e.g., 30-stage1-implementation-report.md) are accepted in place of the
    exact filename (e.g., 30-implementation-report.md) for phases that support
    stage-indexed artifacts.

    For the code-review phase, the fix report (41-fix-report.md) is only
    required when the review produced findings or a `needs revision` verdict.
    """
    findings: list[Finding] = []
    staged_mode = _is_staged_mode(run_dir)
    artifacts = _required_artifacts(run_dir, phase, staged_mode)
    for filename, _sections in artifacts:
        if _resolve_artifact_path(run_dir, filename, phase, staged_mode) is not None:
            continue  # Exact or stage-indexed variant found
        findings.append(
            Finding(
                severity="error",
                check="artifact_structure",
                message=f"Required artifact missing: {filename}",
            )
        )
    return findings


def check_artifact_sections(run_dir: Path, phase: str) -> list[Finding]:
    """Check that existing artifacts contain required sections.

    In staged mode, stage-indexed variants are checked for required sections
    when the exact filename is not present.
    """
    findings: list[Finding] = []
    staged_mode = _is_staged_mode(run_dir)
    artifacts = _required_artifacts(run_dir, phase, staged_mode)
    for filename, required_sections in artifacts:
        path = _resolve_artifact_path(run_dir, filename, phase, staged_mode)
        if path is None:
            continue  # Already reported by check_artifacts_exist
        text = path.read_text(encoding="utf-8")
        for section in required_sections:
            if not _section_present(text, section):
                findings.append(
                    Finding(
                        severity="error",
                        check="artifact_structure",
                        message=f"Required section missing in {path.name}: {section}",
                    )
                )
    return findings


def check_artifact_naming(run_dir: Path) -> list[Finding]:
    """Check that artifact filenames follow the phase-grouped numbering scheme."""
    findings: list[Finding] = []
    valid_prefixes = {"00", "01", "02", "10", "11", "12", "13", "14", "15", "20", "21", "22", "23",
                      "30", "31", "32", "33", "40", "41", "42", "43", "50"}
    for path in run_dir.iterdir():
        if not path.is_file() or not path.name.endswith(".md"):
            continue
        if path.name.startswith("back-"):
            continue  # Backward handoff packets validated separately
        prefix = path.name[:2]
        if prefix not in valid_prefixes:
            findings.append(
                Finding(
                    severity="warning",
                    check="artifact_structure",
                    message=f"Filename does not match phase-grouped numbering: {path.name}",
                )
            )
    return findings


def run_all(run_dir: Path, phase: str) -> list[Finding]:
    """Run all artifact structure checks for a phase."""
    findings: list[Finding] = []
    findings.extend(check_artifacts_exist(run_dir, phase))
    findings.extend(check_artifact_sections(run_dir, phase))
    findings.extend(check_artifact_naming(run_dir))
    return findings
