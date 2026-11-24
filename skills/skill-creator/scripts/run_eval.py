#!/usr/bin/env python3
"""Trigger evaluation for a skill description, run by native subagents.

This script spawns no CLI. An agent with subagent support runs it in two steps:

1. --emit-tasks OUT: write one task per (query, run). Each task holds a
   self-contained prompt that shows a fresh subagent only the skill's name and
   description and asks for a YES/NO decision. Subagents must not use tools.
2. --score TASKS --responses RESP: parse the subagents' answers (a JSON object
   mapping task id to answer text) and compute per-query trigger rates.

This is a proxy. It measures whether a model reading the description would
choose the skill, not Claude Code's real routing.
"""

import argparse
import json
import re
import sys
from pathlib import Path

from scripts.utils import parse_skill_md


def build_task_prompt(skill_name: str, description: str, query: str) -> str:
    return (
        "You are deciding whether an AI coding agent would load a skill to handle a user request.\n\n"
        "Available skill:\n"
        f"- name: {skill_name}\n"
        f"- description: {description}\n\n"
        "User request:\n"
        f"<request>\n{query}\n</request>\n\n"
        "Based only on the skill's name and description, would the agent load this skill "
        "to handle the request? Do not use any tools. Answer with exactly one word: YES or NO."
    )


def parse_decision(text: str | None) -> bool | None:
    """Return True for YES, False for NO, None when the first word is neither."""
    words = re.findall(r"[A-Za-z]+", text or "")
    if not words:
        return None
    first = words[0].upper()
    if first == "YES":
        return True
    if first == "NO":
        return False
    return None


def build_tasks(
    eval_set: list[dict],
    skill_name: str,
    description: str,
    runs_per_query: int,
    trigger_threshold: float,
) -> dict:
    tasks = []
    for q_idx, item in enumerate(eval_set):
        for run_idx in range(runs_per_query):
            tasks.append({
                "id": f"{q_idx}-{run_idx}",
                "query": item["query"],
                "should_trigger": item["should_trigger"],
                "prompt": build_task_prompt(skill_name, description, item["query"]),
            })
    return {
        "skill_name": skill_name,
        "description": description,
        "runs_per_query": runs_per_query,
        "trigger_threshold": trigger_threshold,
        "tasks": tasks,
    }


def score_responses(tasks_doc: dict, responses: dict[str, str]) -> dict:
    """Score subagent answers. Queries with any missing or unparseable answer are
    reported as incomplete and never counted as passes or failures."""
    grouped: dict[str, dict] = {}
    for task in tasks_doc["tasks"]:
        entry = grouped.setdefault(
            task["query"],
            {"should_trigger": task["should_trigger"], "decisions": [], "missing": 0},
        )
        decision = parse_decision(responses.get(task["id"]))
        if decision is None:
            entry["missing"] += 1
        else:
            entry["decisions"].append(decision)

    threshold = tasks_doc["trigger_threshold"]
    results = []
    incomplete = []
    for query, entry in grouped.items():
        if entry["missing"]:
            incomplete.append({"query": query, "missing_runs": entry["missing"]})
            continue
        decisions = entry["decisions"]
        triggers = sum(decisions)
        trigger_rate = triggers / len(decisions)
        if entry["should_trigger"]:
            did_pass = trigger_rate >= threshold
        else:
            did_pass = trigger_rate < threshold
        results.append({
            "query": query,
            "should_trigger": entry["should_trigger"],
            "trigger_rate": trigger_rate,
            "triggers": triggers,
            "runs": len(decisions),
            "pass": did_pass,
        })

    passed = sum(1 for r in results if r["pass"])
    return {
        "skill_name": tasks_doc["skill_name"],
        "description": tasks_doc["description"],
        "results": results,
        "summary": {
            "total": len(results),
            "passed": passed,
            "failed": len(results) - passed,
            "incomplete": incomplete,
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Trigger evaluation for a skill description (subagent-driven)")
    parser.add_argument("--eval-set", required=True, help="Path to eval set JSON file")
    parser.add_argument("--skill-path", required=True, help="Path to skill directory")
    parser.add_argument("--description", default=None, help="Override description to test")
    parser.add_argument("--runs-per-query", type=int, default=3, help="Number of runs per query")
    parser.add_argument("--trigger-threshold", type=float, default=0.5, help="Trigger rate threshold")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--emit-tasks", metavar="OUT", help="Write subagent tasks JSON to OUT")
    mode.add_argument("--score", metavar="TASKS", help="Score responses for the tasks file TASKS (requires --responses)")
    parser.add_argument("--responses", help="JSON object mapping task id to subagent answer text (with --score)")
    args = parser.parse_args()

    skill_path = Path(args.skill_path)
    if not (skill_path / "SKILL.md").exists():
        print(f"Error: No SKILL.md found at {skill_path}", file=sys.stderr)
        sys.exit(1)

    if args.emit_tasks:
        name, original_description, _ = parse_skill_md(skill_path)
        description = args.description or original_description
        eval_set = json.loads(Path(args.eval_set).read_text())
        tasks_doc = build_tasks(eval_set, name, description, args.runs_per_query, args.trigger_threshold)
        Path(args.emit_tasks).write_text(json.dumps(tasks_doc, indent=2))
        print(f"Wrote {len(tasks_doc['tasks'])} tasks to {args.emit_tasks}", file=sys.stderr)
        return

    if not args.responses:
        parser.error("--score requires --responses")
    tasks_doc = json.loads(Path(args.score).read_text())
    responses = json.loads(Path(args.responses).read_text())
    output = score_responses(tasks_doc, responses)
    incomplete = output["summary"]["incomplete"]
    print(json.dumps(output, indent=2))
    if incomplete:
        print(
            f"Warning: {len(incomplete)} queries have missing or unparseable answers; "
            f"re-run those task ids before trusting the score.",
            file=sys.stderr,
        )
        sys.exit(2)


if __name__ == "__main__":
    main()
