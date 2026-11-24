#!/usr/bin/env python3
"""Tests for subagent-driven run_eval scoring and improve_description parsing."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent


def load_module(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS_DIR / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


run_eval = load_module("run_eval")
improve = load_module("improve_description")


class ParseDecisionTests(unittest.TestCase):
    def test_yes_and_no(self):
        self.assertIs(run_eval.parse_decision("YES"), True)
        self.assertIs(run_eval.parse_decision("no."), False)

    def test_unparseable_answer_is_missing(self):
        self.assertIsNone(run_eval.parse_decision(""))
        self.assertIsNone(run_eval.parse_decision("maybe"))


class ScoreResponsesTests(unittest.TestCase):
    def setUp(self):
        self.tasks_doc = {
            "skill_name": "demo",
            "description": "d",
            "trigger_threshold": 0.5,
            "tasks": [
                {"id": "0-0", "query": "q1", "should_trigger": True},
                {"id": "0-1", "query": "q1", "should_trigger": True},
                {"id": "1-0", "query": "q2", "should_trigger": False},
                {"id": "2-0", "query": "q3", "should_trigger": True},
            ],
        }

    def test_threshold_math(self):
        responses = {"0-0": "YES", "0-1": "NO", "1-0": "NO", "2-0": "YES"}
        result = run_eval.score_responses(self.tasks_doc, responses)
        by_query = {r["query"]: r for r in result["results"]}
        self.assertTrue(by_query["q1"]["pass"])   # 1/2 >= 0.5
        self.assertTrue(by_query["q2"]["pass"])   # 0/1 < 0.5
        self.assertEqual(result["summary"]["total"], 3)
        self.assertEqual(result["summary"]["incomplete"], [])

    def test_missing_answer_is_incomplete_not_pass(self):
        responses = {"0-0": "YES", "0-1": "YES", "1-0": "NO"}  # q3 has no answer
        result = run_eval.score_responses(self.tasks_doc, responses)
        self.assertEqual([i["query"] for i in result["summary"]["incomplete"]], ["q3"])
        self.assertNotIn("q3", {r["query"] for r in result["results"]})
        self.assertEqual(result["summary"]["total"], 2)


class ImproveParserTests(unittest.TestCase):
    def test_extracts_tagged_description(self):
        text = "Here you go.\n<new_description>Use this skill for PDFs.</new_description>"
        self.assertEqual(improve.parse_description(text), "Use this skill for PDFs.")

    def test_falls_back_to_whole_reply(self):
        self.assertEqual(improve.parse_description('  "Plain text"  '), "Plain text")

    def test_shorten_prompt_reports_length(self):
        long_desc = "x" * (improve.DESCRIPTION_LIMIT + 1)
        prompt = improve.build_shorten_prompt("BASE", long_desc)
        self.assertIn(str(len(long_desc)), prompt)
        self.assertTrue(prompt.startswith("BASE"))


if __name__ == "__main__":
    unittest.main()
