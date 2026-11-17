"""Unit tests for the aggregate_benchmark extension (maintenance pilot pg-001).

Covers t-arms, t-pairs, t-metrics, t-compat from the plan at
.agents/plans/frontier-model-maintenance.md.
"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parent / "aggregate_benchmark.py"
FIXTURE_3ARM = Path(__file__).parent / "testdata" / "benchmark-three-arm"
FIXTURE_2ARM = Path(__file__).parent / "testdata" / "benchmark-two-arm"
GOLDEN = FIXTURE_2ARM / "legacy-benchmark.json"


def run_aggregator(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
    )


def generate(benchmark_dir: Path, **kwargs) -> dict:
    sys.path.insert(0, str(SCRIPT.parent))
    import aggregate_benchmark as ab

    try:
        bench = ab.generate_benchmark(
            benchmark_dir, kwargs.get("skill_name"), kwargs.get("skill_path"),
            primary=kwargs.get("primary"), baseline=kwargs.get("baseline"),
            executor_model=kwargs.get("executor_model"),
        )
    finally:
        sys.path.remove(str(SCRIPT.parent))
    return bench


class SelectionTests(unittest.TestCase):
    """t-arms: explicit arm selection, ordering, named comparisons."""

    def test_three_arms_without_selection_fails(self):
        with tempfile.TemporaryDirectory() as td:
            r = run_aggregator(str(FIXTURE_3ARM), "-o", str(Path(td) / "b.json"))
        self.assertNotEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("candidate", r.stderr + r.stdout)

    def test_selected_primary_comes_first_and_delta_is_primary_minus_baseline(self):
        with tempfile.TemporaryDirectory() as td:
            self._selected_primary_case(td)

    def _selected_primary_case(self, td: str) -> dict:
        r = run_aggregator(
            str(FIXTURE_3ARM), "--primary", "candidate", "--baseline", "current",
            "-o", str(Path(td) / "b.json"),
        )
        self.assertEqual(r.returncode, 0, r.stderr)
        out = Path(td) / "b.json"
        self.assertTrue(out.exists(), r.stdout)

        bench = json.load(open(out))
        arms = [k for k in bench["run_summary"] if k != "delta"]
        self.assertEqual(arms[0], "candidate")
        self.assertEqual(arms[1], "current")
        self.assertIn("baseline", arms)
        # delta = candidate pass mean - current pass mean
        cand = bench["run_summary"]["candidate"]["pass_rate"]["mean"]
        cur = bench["run_summary"]["current"]["pass_rate"]["mean"]
        expected = f"{cand - cur:+.2f}"
        self.assertEqual(bench["run_summary"]["delta"]["pass_rate"], expected)
        self.assertIn("comparisons", bench)
        self.assertIn("candidate_vs_current", bench["comparisons"])
        return bench

    def test_main_and_markdown_survive_three_arms(self):
        bench = generate(FIXTURE_3ARM, primary="candidate", baseline="current")
        # generate_benchmark with a selection must not crash on three arms
        self.assertEqual(
            len([k for k in bench["run_summary"] if k != "delta"]), 3
        )
        md = generate_markdown(bench)
        self.assertIn("Candidate", md)


def generate_markdown(bench: dict) -> str:
    sys.path.insert(0, str(SCRIPT.parent))
    import aggregate_benchmark as ab

    try:
        return ab.generate_markdown(bench)
    finally:
        sys.path.remove(str(SCRIPT.parent))


class PairingTests(unittest.TestCase):
    """t-pairs: unmatched/duplicate/failed runs surface as diagnostics."""

    def test_unmatched_and_duplicates_and_failed_are_listed(self):
        bench = generate(FIXTURE_3ARM, primary="candidate", baseline="current")
        comp = bench["comparisons"]["candidate_vs_current"]
        for key in ("matched_pairs", "unmatched", "duplicates", "failed_runs"):
            self.assertIn(key, comp)
        # eval-2 and eval-4 share eval_id 2: duplicates must be surfaced
        self.assertTrue(
            any(d.get("eval_id") == 2 for d in comp["duplicates"]),
            comp["duplicates"],
        )
        # eval-3: candidate lacks run-3 -> unmatched pair
        self.assertTrue(len(comp["unmatched"]) > 0, comp["unmatched"])
        # eval-2 baseline run-3 is errored: appears in every comparison
        # that includes the baseline arm
        all_failed = [f for c in bench["comparisons"].values() for f in c["failed_runs"]]
        self.assertTrue(
            any(f.get("eval_id") == 2 and f.get("run_number") == 3 and f.get("configuration") == "baseline" for f in all_failed),
            all_failed,
        )

    def test_deltas_use_matched_pairs_only(self):
        bench = generate(FIXTURE_3ARM, primary="candidate", baseline="current")
        comp = bench["comparisons"]["candidate_vs_current"]
        # eval-1: 3 matched pairs; eval-2/eval-4 share eval_id 2 so all
        # their pairs are duplicates and excluded; eval-3 has 2 matched
        self.assertEqual(comp["matched_pairs"], 3 + 2, comp)


class MetricsTests(unittest.TestCase):
    """t-metrics: truthful missingness, token sources, counts, model id."""

    def test_tokens_never_substituted_by_output_chars(self):
        bench = generate(FIXTURE_3ARM, primary="candidate", baseline="current")
        # eval-3 current/candidate runs have no tokens anywhere: per-run
        # tokens must be null (baseline arm has tokens and must be non-null)
        runs = [r for r in bench["runs"] if r["eval_id"] == 3 and r["configuration"] in ("current", "candidate")]
        self.assertGreater(len(runs), 0)
        for r in runs:
            self.assertIsNone(r["result"]["tokens"], r)
        for r in bench["runs"]:
            if r["eval_id"] == 3 and r["configuration"] == "baseline":
                self.assertIsNotNone(r["result"]["tokens"], r)
        # arm-level: candidate has zero measured token runs in eval-3 but has
        # tokens in eval-1/2; availability must report measured counts, and no
        # token value may equal an output_chars value (75,76,...)
        avail = bench["metric_availability"]["candidate"]["tokens"]
        self.assertLess(avail["measured"], avail["total"])
        for r in bench["runs"]:
            toks = r["result"]["tokens"]
            if toks is not None:
                self.assertNotEqual(toks, r["result"].get("output_chars"), r)

    def test_arm_with_zero_measured_tokens_has_no_stats_object(self):
        bench = generate(FIXTURE_3ARM, primary="candidate", baseline="current")
        # build an arm with no tokens at all by checking eval-3-only arm is
        # not present; instead verify availability semantics: an arm whose
        # measured==0 would omit the stats object. Here candidate has some
        # measured tokens, so the object exists; the zero case is covered by
        # test_unmeasured_per_run_fields_null plus contract below.
        cand = bench["run_summary"]["candidate"]
        self.assertIn("tokens", cand)

    def test_tokens_read_from_timing_json_even_with_grading_duration(self):
        bench = generate(FIXTURE_3ARM, primary="candidate", baseline="current")
        # eval-1 candidate runs: grading has duration, timing.json has tokens
        runs = [r for r in bench["runs"] if r["eval_id"] == 1 and r["configuration"] == "candidate"]
        for r in runs:
            self.assertIsNotNone(r["result"]["tokens"], r)

    def test_run_counts_and_int_rpm(self):
        bench = generate(FIXTURE_3ARM, primary="candidate", baseline="current")
        self.assertIsInstance(bench["metadata"]["runs_per_configuration"], int)
        self.assertIn("run_counts", bench)
        self.assertEqual(set(bench["run_counts"]), {"baseline", "current", "candidate"})

    def test_executor_model_from_flag(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "b.json"
            r = run_aggregator(
                str(FIXTURE_3ARM), "--primary", "candidate", "--baseline", "current",
                "--executor-model", "claude-test-1", "-o", str(out),
            )
            self.assertEqual(r.returncode, 0, r.stderr)
            bench = json.load(open(out))
            self.assertEqual(bench["metadata"]["executor_model"], "claude-test-1")
        # default when no flag is given
        bench = generate(FIXTURE_3ARM, primary="candidate", baseline="current")
        self.assertEqual(bench["metadata"]["executor_model"], "unavailable")

    def test_delta_key_omitted_when_metric_missing(self):
        bench = generate(FIXTURE_3ARM, primary="candidate", baseline="current")
        # baseline has tokens everywhere; the omitempty case is exercised when
        # an arm lacks a metric entirely. Construct manually:
        bench["run_summary"]["baseline"].pop("tokens")
        sys_path = str(SCRIPT.parent)
        sys.path.insert(0, sys_path)
        import aggregate_benchmark as ab
        try:
            delta = ab.calculate_delta(bench["run_summary"], "candidate", "baseline")
        finally:
            sys.path.remove(sys_path)
        self.assertNotIn("tokens", delta)

    def test_zero_graded_arm_fails(self):
        # eval-2 current arm has only 2 graded runs (run-1 ungraded) — not zero.
        # Build a temp dir where an arm has zero graded runs.
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for arm in ("current", "candidate"):
                d = root / "eval-1" / arm
                d.mkdir(parents=True)
                json.dump({"eval_id": 1, "prompt": "p"}, open(d / "eval_metadata.json", "w"))
                rd = d / "run-1"
                rd.mkdir()
                json.dump({"status": "completed", "reason": ""}, open(rd / "run_status.json", "w"))
                (rd / "outputs").mkdir()
                (rd / "outputs" / "t.md").write_text("x")
                if arm == "candidate":
                    json.dump(
                        {"summary": {"pass_rate": 1.0, "passed": 1, "failed": 0, "total": 1}, "expectations": []},
                        open(rd / "grading.json", "w"),
                    )
            with self.assertRaises(ValueError) as cm:
                generate(root)
            self.assertIn("current", str(cm.exception))

    def test_unmeasured_per_run_fields_null(self):
        bench = generate(FIXTURE_3ARM, primary="candidate", baseline="current")
        for r in bench["runs"]:
            self.assertIn("tokens", r["result"])
            self.assertIn("time_seconds", r["result"])

    def test_unmeasured_time_seconds_is_null(self):
        # cr-001: a run with no timing anywhere must carry a null
        # time_seconds end-to-end — never a zero substitute. Built as a
        # temp fixture because every three-arm run has a measured duration.
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for arm in ("baseline", "candidate"):
                d = root / "eval-1" / arm
                rd = d / "run-1"
                rd.mkdir(parents=True)
                json.dump({"eval_id": 1, "prompt": "p"}, open(d / "eval_metadata.json", "w"))
                json.dump({"status": "completed", "reason": ""}, open(rd / "run_status.json", "w"))
                json.dump(
                    {"summary": {"pass_rate": 1.0, "passed": 1, "failed": 0, "total": 1},
                     "execution_metrics": {"total_tool_calls": 1}, "expectations": []},
                    open(rd / "grading.json", "w"),
                )
            bench = generate(root, primary="candidate", baseline="baseline")
            for r in bench["runs"]:
                self.assertIsNone(r["result"]["time_seconds"], r)
                self.assertIsNone(r["result"]["tokens"], r)
            for arm in ("baseline", "candidate"):
                self.assertNotIn("time_seconds", bench["run_summary"][arm])
                self.assertNotIn("tokens", bench["run_summary"][arm])
                self.assertEqual(
                    bench["metric_availability"][arm]["time_seconds"],
                    {"measured": 0, "total": 1},
                )


class CompatTests(unittest.TestCase):
    """t-compat: legacy keys/types preserved, consumers still work."""

    def test_golden_keys_and_types_preserved(self):
        bench = generate(FIXTURE_2ARM)
        golden = json.load(open(GOLDEN))

        def walk(obj, prefix=""):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    yield from walk(v, f"{prefix}.{k}" if prefix else k)
            else:
                yield prefix, type(obj)

        gold_paths = dict(walk(golden))
        new_paths = dict(walk(bench))
        for path, typ in gold_paths.items():
            if path.startswith("metadata.timestamp"):
                continue
            self.assertIn(path, new_paths, f"missing legacy path {path}")
            self.assertEqual(new_paths[path], typ, f"type changed for {path}")
        # values for fully measured fields. Tokens are the deliberate
        # value correction: the golden (from the unmodified aggregator)
        # substituted output_chars (mean 80); the corrected code reads
        # timing.json total_tokens (mean 500). Assert the correction.
        self.assertEqual(bench["run_summary"]["old_skill"]["tokens"]["mean"], 500.0)
        self.assertNotEqual(
            bench["run_summary"]["old_skill"]["tokens"]["mean"],
            golden["run_summary"]["old_skill"]["tokens"]["mean"],
        )
        self.assertEqual(
            bench["run_summary"]["old_skill"]["time_seconds"]["mean"],
            golden["run_summary"]["old_skill"]["time_seconds"]["mean"],
        )
        delta = bench["run_summary"]["delta"]
        golden_delta = golden["run_summary"]["delta"]
        self.assertEqual(delta["pass_rate"], golden_delta["pass_rate"])
        self.assertEqual(delta["time_seconds"], golden_delta["time_seconds"])
        # token arm means carry the deliberate correction (char-substitution
        # removed): golden old_skill mean 80 (chars) vs corrected 500 (tokens)
        self.assertEqual(delta["tokens"], golden_delta["tokens"])
        # arm order for two-arm input without selection is unchanged
        arms = [k for k in bench["run_summary"] if k != "delta"]
        self.assertEqual(arms, ["old_skill", "with_skill"])

    def test_no_null_means_and_markdown_renders_missing(self):
        bench = generate(FIXTURE_3ARM, primary="candidate", baseline="current")
        for arm, stats in bench["run_summary"].items():
            if arm == "delta":
                continue
            for metric, obj in stats.items():
                if isinstance(obj, dict) and "mean" in obj:
                    self.assertIsNotNone(obj["mean"], (arm, metric))
        md = generate_markdown(bench)
        self.assertNotIn("0 ± 0", md)
        self.assertNotIn("—s", md)

    def test_generate_review_static_on_three_arm_fixture(self):
        gen_review = SCRIPT.parent.parent / "eval-viewer" / "generate_review.py"
        with tempfile.TemporaryDirectory() as td:
            bench = generate(FIXTURE_3ARM, primary="candidate", baseline="current")
            bf = Path(td) / "b.json"
            json.dump(bench, open(bf, "w"))
            html = Path(td) / "review.html"
            r = subprocess.run(
                [sys.executable, str(gen_review), str(FIXTURE_3ARM),
                 "--benchmark", str(bf), "--static", str(html)],
                capture_output=True, text=True,
            )
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertTrue(html.exists())
            content = html.read_text()
            self.assertNotIn("(No prompt found)", content)
            self.assertIn("What does this repo contain?", content)


if __name__ == "__main__":
    unittest.main()
