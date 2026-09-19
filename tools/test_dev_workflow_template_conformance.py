#!/usr/bin/env python3
"""Tests for the second dev-workflow harness review round (template conformance).

Each test renders the bootstrap template that produces a phase artifact and
asserts the deterministic validators accept it — closing the gap where every
template was authored by hand and never conformance-tested (dw-013's test gap).

Covers:
- dw-014: numbered template headings satisfy unnumbered required-section
  checks (artifact_checks + handoff_checks, via _section_present)
- dw-015: checker templates yield a matchable verdict via extract_verdict
  (bracketed placeholder lines are stripped to a single value)
- dw-016: pre-flight runs handoff consumer-ready checks transitively
  (check_pre_phase PRE_FLIGHT_HANDOFF_CHECKS)
- dw-017: /dev-workflow-review round-1 ordering is checker-first (prose
  contract; asserted as text to keep the command file in sync with the
  orchestrator's Code Review exception)

Template paths are the bootstrap sources under skills/ (source of truth);
the installed .ai/skills copies are refreshed from them by the install
scripts and are asserted in-sync here as a guard.
"""

from __future__ import annotations

import re
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / ".ai" / "tools" / "dev-workflow"))

from checks import artifact_checks  # type: ignore[import-not-found]
from checks import handoff_checks  # type: ignore[import-not-found]
from checks.verdicts import extract_verdict, match_verdict, lookup_verdicts_for_filename, CHECKER_VERDICTS  # type: ignore[import-not-found]
import check_pre_phase  # type: ignore[import-not-found]


def _template_body(path: Path) -> str:
    """Return the template's rendered body: the content of the first ```markdown fence."""
    text = path.read_text(encoding="utf-8")
    match = re.search(r"```markdown\n(.*?)```", text, re.DOTALL)
    return match.group(1) if match else text


# Bootstrap template that produces each phase artifact.
TEMPLATES: dict[str, Path] = {
    "02-requirement-ledger.md": REPO_ROOT / "skills" / "dev-workflow-orchestrator" / "references" / "requirement-ledger-template.md",
    "10-research-report.md": REPO_ROOT / "skills" / "research-guide" / "references" / "research-report-template.md",
    "11-research-review.md": REPO_ROOT / "skills" / "research-reviewer" / "references" / "review-report-template.md",
    "20-implementation-plan.md": REPO_ROOT / "skills" / "plan-guide" / "references" / "implementation-plan-template.md",
    "21-plan-review.md": REPO_ROOT / "skills" / "plan-reviewer" / "references" / "review-report-template.md",
    "30-implementation-report.md": REPO_ROOT / "skills" / "plan-executor" / "references" / "implementation-report-template.md",
    "31-implementation-audit.md": REPO_ROOT / "skills" / "implementation-auditor" / "references" / "audit-report-template.md",
    "40-code-review.md": REPO_ROOT / "skills" / "code-reviewer" / "references" / "review-report-template.md",
}


class TemplateSyncTests(unittest.TestCase):
    """dw-014 guard: bootstrap templates and installed .ai copies are in sync."""

    def test_bootstrap_and_installed_templates_in_sync(self) -> None:
        for filename, bootstrap in TEMPLATES.items():
            skill = bootstrap.relative_to(REPO_ROOT / "skills").parts[0]
            installed = REPO_ROOT / ".ai" / "skills" / skill / "references" / bootstrap.name
            if not installed.exists():
                continue  # Not every skill is installed in this checkout
            self.assertEqual(
                bootstrap.read_text(encoding="utf-8"),
                installed.read_text(encoding="utf-8"),
                f"{bootstrap} has diverged from {installed}",
            )


class TemplateSectionConformanceTests(unittest.TestCase):
    """dw-014: templates satisfy the required-section checks, numbered or not."""

    def _assert_sections(self, filename: str, required: list[str], body: str) -> None:
        for section in required:
            self.assertTrue(
                artifact_checks._section_present(body, section),
                f"{filename}: required section not matched (numbered or unnumbered): {section}",
            )

    def test_phase_artifact_templates_satisfy_required_sections(self) -> None:
        for phase, artifacts in artifact_checks.PHASE_ARTIFACTS.items():
            for filename, required in artifacts:
                if filename not in TEMPLATES:
                    continue  # e.g. 50-commit.md has no template
                self._assert_sections(filename, required, _template_body(TEMPLATES[filename]))

    def test_handoff_consumer_sections_satisfiable_from_templates(self) -> None:
        pairs = [
            ("10-research-report.md", handoff_checks.RESEARCH_REPORT_FOR_PLAN),
            ("20-implementation-plan.md", handoff_checks.PLAN_FOR_EXECUTOR),
            ("30-implementation-report.md", handoff_checks.IMPL_REPORT_FOR_REVIEW),
        ]
        for filename, required in pairs:
            self._assert_sections(filename, required, _template_body(TEMPLATES[filename]))

    def test_numbered_heading_variant_matching(self) -> None:
        # Unit-level: _heading_variants returns the unnumbered + numbered forms.
        self.assertEqual(
            artifact_checks._heading_variants("## Problem statement"),
            ["## Problem statement", "## N. Problem statement"],
        )
        self.assertTrue(
            artifact_checks._section_present("## 3. Problem statement\n", "## Problem statement")
        )
        self.assertFalse(
            artifact_checks._section_present("## Problem Statements\n", "## Problem statement")
        )


class TemplateVerdictConformanceTests(unittest.TestCase):
    """dw-015: checker templates yield a matchable verdict via extract_verdict."""

    def test_checker_templates_produce_matchable_verdicts(self) -> None:
        for filename, path in TEMPLATES.items():
            if filename not in CHECKER_VERDICTS:
                continue
            verdict = extract_verdict(_template_body(path))
            valid = lookup_verdicts_for_filename(filename, CHECKER_VERDICTS)
            self.assertIsNotNone(verdict, f"{filename}: no verdict extracted from template")
            self.assertTrue(
                match_verdict(verdict, valid),
                f"{filename}: template verdict {verdict!r} matches none of {sorted(valid)}",
            )

    def test_bracketed_placeholder_stripped_to_single_value(self) -> None:
        # Unit-level: a bracketed placeholder line extracts as one of the options.
        verdict = extract_verdict("## Verdict\n\n<pass | pass with risks | blocked | fail>\n")
        self.assertEqual(verdict, "pass")
        verdict = extract_verdict("## 1. Verdict\n- Verdict: <ready | conditionally ready | needs revision | blocked — choose exactly one>\n")
        self.assertEqual(verdict, "ready")


class PreFlightHandoffTests(unittest.TestCase):
    """dw-016: pre-flight runs handoff consumer-ready checks transitively."""

    def _write(self, run_dir: Path, filename: str, text: str) -> None:
        (run_dir / filename).write_text(text, encoding="utf-8")

    def test_plan_pre_flight_rejects_research_report_missing_sections(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            self._write(run_dir, "00-run-manifest.md", "# Run Manifest\n\n## Run metadata\n- Run mode: linear\n")
            # Research report exists but lacks the sections plan-guide needs.
            self._write(run_dir, "10-research-report.md", "# Research Report\n\nbody only\n")
            findings = check_pre_phase.run_pre_flight(run_dir, "plan")
            self.assertTrue(
                any(f.check == "handoff_integrity" for f in findings),
                "pre-flight must run consumer-ready checks on the research report",
            )

    def test_implement_pre_flight_rejects_plan_missing_sections(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            self._write(run_dir, "00-run-manifest.md", "# Run Manifest\n\n## Run metadata\n- Run mode: linear\n")
            self._write(run_dir, "20-implementation-plan.md", "# Implementation Plan\n\nbody only\n")
            findings = check_pre_phase.run_pre_flight(run_dir, "implement")
            self.assertTrue(
                any(f.check == "handoff_integrity" for f in findings),
                "pre-flight must run consumer-ready checks on the plan",
            )

    def test_pre_flight_passes_on_consumer_ready_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            self._write(run_dir, "00-run-manifest.md", "# Run Manifest\n\n## Run metadata\n- Run mode: linear\n")
            self._write(run_dir, "10-research-report.md", _template_body(TEMPLATES["10-research-report.md"]))
            findings = check_pre_phase.run_pre_flight(run_dir, "plan")
            self.assertFalse([f for f in findings if f.severity == "error"])


class CommandContractTests(unittest.TestCase):
    """dw-017: the review phase command keeps the orchestrator's round-1 ordering."""

    def test_review_command_checker_first_on_round_one(self) -> None:
        text = (REPO_ROOT / "commands" / "dev-workflow-review" / "COMMAND.md").read_text(encoding="utf-8")
        self.assertIn("Round-1 ordering (Code Review exception)", text)
        checker_pos = text.find("**Checker pass (round 1)**")
        doer_pos = text.find("**Doer pass**")
        self.assertGreater(checker_pos, -1, "review command must name a round-1 checker pass")
        self.assertGreater(doer_pos, -1, "review command must name a doer pass")
        self.assertLess(checker_pos, doer_pos, "round 1 must run the checker before the doer")


if __name__ == "__main__":
    unittest.main()
