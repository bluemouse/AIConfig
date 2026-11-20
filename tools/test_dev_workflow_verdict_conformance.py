#!/usr/bin/env python3
"""Cross-layer verdict-conformance tests for the dev-workflow harness (ar-008).

verdicts.py is the machine-readable source of truth for checker verdict
vocabularies. The vocabularies are duplicated as prose in four other layers;
nothing previously diffed those layers against verdicts.py, so drift passed
the full test suite (exactly what ar-002/ar-003/ar-006 were). This test pins:

1. Each checker agent's AGENT.md Output-format verdict list
   == CHECKER_VERDICTS for its phase artifact.
2. Each checker skill's SKILL.md verdict instruction
   == CHECKER_VERDICTS for its phase artifact.
3. Each per-phase command's route bullets cover ACCEPT / REVISE / BLOCKED
   verdicts for its phase (and only verdicts in CHECKER_VERDICTS).
4. loop-contracts.md's per-loop rows agree with ACCEPT/REVISE/BLOCKED sets.
5. plan-reviewer's agent documents the stage-exit exception (32-stage*
   verdicts: plan-current / plan-stale).

Run from the repository root: python tools/test_dev_workflow_verdict_conformance.py
"""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "skills" / "dev-workflow-orchestrator" / "scripts" / "checks"))

import verdicts  # noqa: E402

AGENTS = {
    "research": "research-reviewer",
    "plan": "plan-reviewer",
    "implement": "implementation-auditor",
    "code-review": "code-reviewer",
}
PHASE_ARTIFACT = {
    "research": "11-research-review.md",
    "plan": "21-plan-review.md",
    "implement": "31-implementation-audit.md",
    "code-review": "40-code-review.md",
}


def _agent_output_format(name: str) -> str:
    """Extract the verdict list of a checker agent's AGENT.md.

    Since the shared-boilerplate fold, the verdict list lives on the
    "Allowed verdicts" line inside the Per-agent contract section (the
    output-format boilerplate moved to
    dev-workflow-orchestrator/references/checker-subagent-contract.md).
    """
    text = (REPO_ROOT / "agents" / name / "AGENT.md").read_text(encoding="utf-8")
    # Capture through wrapped continuation lines until the next bullet or
    # the stage-exit exception sentence.
    match = re.search(
        r"\*\*Allowed verdicts:\*\*(.*?)(?=\n- |\n\n|\*\*Stage-exit exception)",
        text,
        re.DOTALL,
    )
    assert match, f"No Allowed verdicts line in agents/{name}/AGENT.md"
    return match.group(1)


def _bullet_verdicts(section: str) -> set[str]:
    """Extract the verdict strings from an Allowed verdicts line."""
    return set(re.findall(r"`([^`]+)`", section))


class AgentVerdictConformanceTests(unittest.TestCase):
    """ar-008 layer 1: agent AGENT.md Output format == verdicts.CHECKER_VERDICTS."""

    def test_agent_verdict_lists_match_verdicts_py(self) -> None:
        for phase, name in AGENTS.items():
            with self.subTest(phase=phase):
                section = _agent_output_format(name)
                expected = verdicts.CHECKER_VERDICTS[PHASE_ARTIFACT[phase]]
                actual = _bullet_verdicts(section)
                self.assertEqual(
                    actual,
                    expected,
                    f"agents/{name}/AGENT.md verdict list {sorted(actual)} != "
                    f"verdicts.py {sorted(expected)} for {PHASE_ARTIFACT[phase]}",
                )

    def test_plan_reviewer_documents_stage_exit_exception(self) -> None:
        """ar-003 pin: plan-reviewer's agent must carry the stage-exit verdict
        exception, since the AGENT.md body is the subagent prompt in native
        dispatch and staged-iterator step 8 dispatches it in stage-exit mode."""
        text = (REPO_ROOT / "agents" / "plan-reviewer" / "AGENT.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("plan-current", text,
                      "plan-reviewer agent missing stage-exit verdict plan-current")
        self.assertIn("plan-stale", text,
                      "plan-reviewer agent missing stage-exit verdict plan-stale")


class SkillVerdictConformanceTests(unittest.TestCase):
    """ar-008 layer 2: checker skill SKILL.md verdict instruction matches."""

    def test_skill_verdict_instruction_matches_verdicts_py(self) -> None:
        # code-reviewer keeps its verdict vocabulary in the report template,
        # not the SKILL.md body; the other three carry it in SKILL.md.
        CODE_REVIEWER_TEMPLATE = (
            REPO_ROOT / "skills" / "code-reviewer" / "references" / "review-report-template.md"
        )
        for phase, name in AGENTS.items():
            with self.subTest(phase=phase):
                sources = [(REPO_ROOT / "skills" / name / "SKILL.md")]
                if phase == "code-review":
                    sources.append(CODE_REVIEWER_TEMPLATE)
                texts = [s.read_text(encoding="utf-8") for s in sources]
                expected = verdicts.CHECKER_VERDICTS[PHASE_ARTIFACT[phase]]
                for v in expected:
                    # cr-007: the verdict must be assigned in an instruction
                    # line — "verdict" within the same line before the
                    # backticked value (the templates' assign/verdict:/
                    # Loop-verdict lines) — not merely mentioned anywhere; a
                    # "never rubber-stamp a ready verdict" sentence does not
                    # match because "verdict" follows the value there.
                    self.assertTrue(
                        any(
                            re.search(
                                rf"verdict[^\n]{{0,80}}?`?{re.escape(v)}`?",
                                text,
                                re.IGNORECASE,
                            )
                            for text in texts
                        ),
                        f"none of {[str(s) for s in sources]} assigns verdict '{v}' "
                        f"required by verdicts.py for {PHASE_ARTIFACT[phase]}",
                    )


class CommandRouteConformanceTests(unittest.TestCase):
    """ar-008 layer 3: per-phase command route bullets cover the verdict sets."""

    def test_command_routes_cover_verdict_sets(self) -> None:
        command_files = {
            "research": REPO_ROOT / "commands" / "research" / "COMMAND.md",
            "plan": REPO_ROOT / "commands" / "plan" / "COMMAND.md",
            "implement": REPO_ROOT / "commands" / "implement" / "COMMAND.md",
            "code-review": REPO_ROOT / "commands" / "review" / "COMMAND.md",
        }
        for phase, path in command_files.items():
            with self.subTest(phase=phase):
                text = path.read_text(encoding="utf-8")
                artifact = PHASE_ARTIFACT[phase]
                accept = verdicts.ACCEPT_VERDICTS[artifact]
                revise = verdicts.REVISE_VERDICTS[artifact]
                blocked = verdicts.BLOCKED_VERDICTS[artifact]
                for v in accept:
                    self.assertIn(
                        f"`{v}`",
                        text,
                        f"{path}: accept verdict '{v}' not routed",
                    )
                for v in revise:
                    self.assertIn(
                        f"`{v}`",
                        text,
                        f"{path}: revise verdict '{v}' not routed",
                    )
                for v in blocked:
                    self.assertIn(
                        f"`{v}`",
                        text,
                        f"{path}: blocked verdict '{v}' not routed",
                    )


class LoopContractConformanceTests(unittest.TestCase):
    """ar-008 layer 4: loop-contracts.md per-loop rows agree with verdicts.py.

    Rows are extracted by the loop's section heading (cr-007), not by
    position in the file — reordering or inserting a loop section must not
    silently misassign vocabularies.
    """

    def _loop_sections(self) -> dict[str, str]:
        """Map loop name → section body, anchored on `## Loop N: <name>` headings."""
        text = (
            REPO_ROOT
            / "skills"
            / "dev-workflow-orchestrator"
            / "references"
            / "loop-contracts.md"
        ).read_text(encoding="utf-8")
        sections: dict[str, str] = {}
        matches = list(
            re.finditer(r"^## Loop \d+: (\w[\w -]*?)\s*(?:\(.*\))?\s*$", text, re.MULTILINE)
        )
        assert matches, "loop-contracts.md missing '## Loop N:' headings"
        for i, match in enumerate(matches):
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            sections[match.group(1).strip().lower()] = text[match.end():end]
        return sections

    def _terminal_labels_row(self, section: str, loop_name: str) -> str:
        rows = re.findall(r"\| Terminal labels \|([^|]+)\|", section)
        assert len(rows) == 1, (
            f"loop-contracts.md Loop '{loop_name}': expected exactly one "
            f"Terminal labels row, found {len(rows)}"
        )
        return rows[0]

    def test_loop_contracts_terminal_labels_match(self) -> None:
        sections = self._loop_sections()
        # Loop 4 (Code Review) and Loop 6 (Final Deep Review) share the same
        # verdict vocabulary; either satisfies the code-review pin.
        loop_names = {
            "research": ["research"],
            "plan": ["plan"],
            "implement": ["implement"],
            "code-review": ["code review", "final deep review"],
        }
        for phase, artifact in PHASE_ARTIFACT.items():
            with self.subTest(phase=phase):
                rows = None
                for name in loop_names[phase]:
                    section = sections.get(name)
                    if section is None:
                        continue
                    rows = self._terminal_labels_row(section, name)
                    break
                assert rows is not None, (
                    f"loop-contracts.md missing a loop section for phase "
                    f"'{phase}' (looked for {loop_names[phase]})"
                )
                for v in verdicts.ACCEPT_VERDICTS[artifact]:
                    self.assertIn(v, rows, f"loop-contracts {phase}: accept verdict '{v}' missing from Terminal labels")
                for v in verdicts.REVISE_VERDICTS[artifact]:
                    self.assertIn(v, rows, f"loop-contracts {phase}: revise verdict '{v}' missing from Terminal labels")
                for v in verdicts.BLOCKED_VERDICTS[artifact]:
                    self.assertIn(v, rows, f"loop-contracts {phase}: blocked verdict '{v}' missing from Terminal labels")


class RootCauseVocabularyConformanceTests(unittest.TestCase):
    """Root-cause-phase vocabulary pins (cr-005): every prose layer that
    documents the field's values must agree with loop_checks.ROOT_CAUSE_VALUES
    and route on real values — never on the rejected 'upstream' label."""

    VALUES = {"local", "research", "clarify", "plan", "implement", "code-review"}

    def test_command_routes_never_use_upstream_value(self) -> None:
        """`upstream` is rejected by the validator (loop_checks vocabulary
        check); command routing bullets must route on real field values."""
        targets = {
            "research": REPO_ROOT / "commands" / "research" / "COMMAND.md",
            "plan": REPO_ROOT / "commands" / "plan" / "COMMAND.md",
            "implement": REPO_ROOT / "commands" / "implement" / "COMMAND.md",
            "code-review": REPO_ROOT / "commands" / "review" / "COMMAND.md",
            # cr-011: the orchestrator's own routing/escalation conditions are
            # held to the same rule — `root-cause-phase` = upstream is
            # unreachable (the validator rejects the value), so routing on it
            # matches nothing.
            "orchestrator": REPO_ROOT / "skills" / "dev-workflow-orchestrator" / "SKILL.md",
        }
        for phase, path in targets.items():
            with self.subTest(phase=phase):
                text = path.read_text(encoding="utf-8")
                self.assertIsNone(
                    re.search(r"root-cause-phase`?\s*[=:]\s*`?upstream", text, re.IGNORECASE),
                    f"{path}: routes on 'upstream', which the validator rejects — "
                    f"route on the actual phase values",
                )
                self.assertIsNone(
                    re.search(r"root-cause-phase:\s*`?upstream", text, re.IGNORECASE),
                    f"{path}: routes on 'upstream', which the validator rejects — "
                    f"route on the actual phase values",
                )

    def test_loop_contracts_root_cause_rows_match(self) -> None:
        """Every loop's Root cause field row lists the full vocabulary."""
        sections = LoopContractConformanceTests()._loop_sections()
        for loop_name in (
            "research",
            "plan",
            "implement",
            "code review",
            "final deep review",
        ):
            with self.subTest(loop=loop_name):
                section = sections.get(loop_name)
                assert section is not None, f"loop-contracts.md missing Loop '{loop_name}'"
                rows = re.findall(r"\| Root cause field \|([^|]+)\|", section)
                assert rows, f"loop-contracts.md Loop '{loop_name}': no Root cause field row"
                for value in self.VALUES:
                    self.assertIn(
                        f"`{value}`",
                        rows[0],
                        f"loop-contracts.md Loop '{loop_name}': root-cause value "
                        f"'{value}' missing from Root cause field row",
                    )

    def test_agent_bodies_document_full_vocabulary(self) -> None:
        """The shared checker-subagent contract (which every checker agent
        loads in its Read-first section) lists the full root-cause vocabulary,
        and each agent delegates to it."""
        contract = (
            REPO_ROOT
            / "skills"
            / "dev-workflow-orchestrator"
            / "references"
            / "checker-subagent-contract.md"
        ).read_text(encoding="utf-8")
        match = re.search(
            r"`root-cause-phase` valid values: (.*?)\.\n",
            contract,
            re.DOTALL,
        )
        assert match, "checker-subagent-contract.md: no root-cause-phase valid-values list"
        listed = set(re.findall(r"`(\w[\w-]*)`", match.group(1)))
        self.assertEqual(
            listed,
            self.VALUES,
            "checker-subagent-contract.md root-cause vocabulary "
            f"{sorted(listed)} != {sorted(self.VALUES)}",
        )
        for phase, name in AGENTS.items():
            with self.subTest(phase=phase):
                text = (REPO_ROOT / "agents" / name / "AGENT.md").read_text(
                    encoding="utf-8"
                )
                self.assertIn(
                    "checker-subagent-contract.md",
                    text,
                    f"agents/{name}/AGENT.md: does not load the shared "
                    "checker contract",
                )

    def test_skill_bodies_and_templates_document_full_vocabulary(self) -> None:
        """cr-012: the checker skill bodies and report templates that carry
        a root-cause-phase value list (all hand-edited for the clarify
        harmonization) list the full vocabulary — these layers are otherwise
        unpinned and would drift silently."""
        cases = {
            # value list ends right before the "Use `local`" guidance sentence
            "skills/plan-reviewer/SKILL.md": (
                r"root-cause-phase` field: (.*?)\. Use `local`",
            ),
            # capture starts at the first value (`local`), gloss included
            "skills/implementation-auditor/references/audit-report-template.md": (
                r"`root-cause-phase`: (`local`.*?)\. Use `local`",
            ),
            # template placeholder list, values unbackticked inside <...>
            "skills/code-reviewer/references/review-report-template.md": (
                r"root-cause-phase: <(.*?)> — use `local`",
            ),
        }
        for rel, (pattern,) in cases.items():
            with self.subTest(source=rel):
                text = (REPO_ROOT / rel).read_text(encoding="utf-8")
                match = re.search(pattern, text)
                assert match, f"{rel}: no root-cause-phase value list found"
                # Each pipe-separated chunk is either "`value` (gloss)" in
                # the prose lists or a bare value in the placeholder list —
                # take the leading backticked token, else the bare chunk.
                listed = set()
                for chunk in match.group(1).split("|"):
                    chunk = chunk.strip()
                    token_match = re.match(r"`?(\w[\w-]*)`?", chunk)
                    if token_match:
                        listed.add(token_match.group(1).lower())
                self.assertEqual(
                    listed,
                    self.VALUES,
                    f"{rel} root-cause vocabulary {sorted(listed)} "
                    f"!= {sorted(self.VALUES)}",
                )


if __name__ == "__main__":
    unittest.main()
