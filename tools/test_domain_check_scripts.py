#!/usr/bin/env python3
"""Regression tests for domain skill check scripts (t-012, t-013)."""

from __future__ import annotations

import contextlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import unittest
import uuid
from collections.abc import Iterator
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
KOTLIN_CHECK = REPO_ROOT / "skills" / "kotlin-coding" / "scripts" / "kotlin_project_check.sh"
GRADLE_CHECK = REPO_ROOT / "skills" / "gradle-dev" / "scripts" / "gradle_project_check.sh"
ANDROID_GRADLE_CHECK = (
    REPO_ROOT / "skills" / "gradle-android-dev" / "scripts" / "android_gradle_project_check.sh"
)
SLANG_MATRIX = REPO_ROOT / "skills" / "slang-dev" / "scripts" / "slang_compile_matrix.py"
COLLECT_GIT_CONTEXT = (
    REPO_ROOT / "skills" / "git-merge-guide" / "scripts" / "collect-git-context.sh"
)
SCRATCH_ROOT = REPO_ROOT / ".pytest_cache" / "domain_script_tests"


@contextlib.contextmanager
def workspace_temp_dir() -> Iterator[Path]:
    """Create and clean up an isolated scratch directory under .pytest_cache/."""
    temp_dir = SCRATCH_ROOT / uuid.uuid4().hex
    temp_dir.mkdir(parents=True, exist_ok=False)
    try:
        yield temp_dir
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
        try:
            SCRATCH_ROOT.rmdir()
        except OSError:
            pass


def load_slang_module():
    spec = importlib.util.spec_from_file_location("slang_compile_matrix", SLANG_MATRIX)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load module from {SLANG_MATRIX}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["slang_compile_matrix"] = module
    spec.loader.exec_module(module)
    return module


class DomainGradleAndKotlinScriptTests(unittest.TestCase):
    """t-012: C-10 fixes for Kotlin and Gradle project check scripts."""

    def test_kotlin_full_dry_run_omits_clean(self) -> None:
        with workspace_temp_dir() as proj:
            (proj / "settings.gradle.kts").write_text('rootProject.name = "demo"\n', encoding="utf-8")
            (proj / "build.gradle.kts").write_text('plugins { kotlin("jvm") }\n', encoding="utf-8")
            gradlew = proj / "gradlew"
            gradlew.write_text(
                "#!/bin/sh\n"
                'if [ "${1:-}" = "tasks" ] || [ "${2:-}" = "tasks" ]; then\n'
                "  printf 'clean - Deletes the build directory.\\n'\n"
                "  printf 'check - Runs all checks.\\n'\n"
                "  printf 'test - Runs the unit tests.\\n'\n"
                "  exit 0\n"
                "fi\n"
                "printf 'INVOKED:%s\\n' \"$*\"\n",
                encoding="utf-8",
            )
            gradlew.chmod(0o755)

            dry = subprocess.run(
                ["bash", str(KOTLIN_CHECK), "--full", "--dry-run", str(proj)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(dry.returncode, 0, msg=dry.stderr)
            tokens = dry.stdout.strip().split()
            self.assertNotIn("clean", tokens, f"--full --dry-run must not schedule clean: {dry.stdout}")
            self.assertIn("check", tokens, f"--full --dry-run should schedule check: {dry.stdout}")

            live = subprocess.run(
                ["bash", str(KOTLIN_CHECK), "--full", str(proj)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(live.returncode, 0, msg=live.stderr)
            self.assertNotIn("clean", live.stdout.split(), f"--full must not run clean: {live.stdout}")
            self.assertIn("INVOKED:check", live.stdout)

    def test_gradle_scripts_preserve_non_executable_gradlew_permissions(self) -> None:
        for script in (GRADLE_CHECK, ANDROID_GRADLE_CHECK):
            with self.subTest(script=script.name), workspace_temp_dir() as proj:
                (proj / "settings.gradle.kts").write_text('rootProject.name = "demo"\n', encoding="utf-8")
                (proj / "build.gradle.kts").write_text("plugins { id(\"java\") }\n", encoding="utf-8")
                gradlew = proj / "gradlew"
                gradlew.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
                gradlew.chmod(0o644)

                res = subprocess.run(
                    ["bash", str(script), "--dry-run", str(proj)],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(res.returncode, 0, msg=res.stderr)
                mode = gradlew.stat().st_mode & 0o777
                self.assertEqual(
                    mode,
                    0o644,
                    f"{script.name} mutated ./gradlew permissions to {oct(mode)}",
                )
                self.assertIn(
                    "sh ./gradlew",
                    res.stdout,
                    f"{script.name} should use 'sh ./gradlew' when ./gradlew is 0644: {res.stdout}",
                )

    def test_android_gradle_check_discovers_flavored_debug_tasks(self) -> None:
        dsl_cases = (
            (
                "build.gradle.kts",
                'plugins { id("com.android.application") }\n'
                'android { productFlavors { create("free") } }\n',
            ),
            (
                "build.gradle",
                "plugins { id 'com.android.application' }\n"
                "android {\n"
                "  productFlavors {\n"
                "    all { minSdk 24 }\n"
                "    free { dimension 'tier' }\n"
                "  }\n"
                "}\n",
            ),
        )
        for build_filename, build_content in dsl_cases:
            with self.subTest(dsl=build_filename), workspace_temp_dir() as proj:
                (proj / "settings.gradle.kts").write_text('rootProject.name = "flavored"\n', encoding="utf-8")
                (proj / build_filename).write_text(build_content, encoding="utf-8")
                invocations_log = proj / "invocations.log"
                gradlew = proj / "gradlew"
                gradlew.write_text(
                    "#!/bin/sh\n"
                    f'printf "%s\\n" "$*" >> "{invocations_log}"\n'
                    "exit 0\n",
                    encoding="utf-8",
                )
                gradlew.chmod(0o755)

                res = subprocess.run(
                    ["bash", str(ANDROID_GRADLE_CHECK), "--dry-run", str(proj)],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(res.returncode, 0, msg=res.stderr)
                self.assertFalse(
                    invocations_log.exists(),
                    "--dry-run must not invoke ./gradlew at all",
                )
                self.assertIn("assembleFreeDebug", res.stdout)
                self.assertIn("testFreeDebugUnitTest", res.stdout)
                self.assertIn("lintFreeDebug", res.stdout)
                self.assertIn("connectedFreeDebugAndroidTest", res.stdout)
                self.assertNotRegex(res.stdout, r"\bassembleDebug\b")
                self.assertNotRegex(res.stdout, r"\btestDebugUnitTest\b")
                self.assertNotRegex(res.stdout, r"\blintDebug\b")

    def test_android_gradle_check_quick_and_full_live_execution(self) -> None:
        with workspace_temp_dir() as proj:
            (proj / "settings.gradle.kts").write_text('rootProject.name = "flavored-live"\n', encoding="utf-8")
            (proj / "build.gradle.kts").write_text(
                'plugins { id("com.android.application") }\n',
                encoding="utf-8",
            )
            invocations_log = proj / "invocations.log"
            gradlew = proj / "gradlew"
            gradlew.write_text(
                "#!/bin/sh\n"
                f'printf "%s\\n" "$*" >> "{invocations_log}"\n'
                'case "$*" in\n'
                '  *"tasks --all"*)\n'
                "    printf 'Build tasks\\n-----------\\n'\n"
                "    printf 'assembleDebug - Assembles main outputs for all Debug variants.\\n'\n"
                "    printf 'assembleFreeDebug - Assembles main outputs for variant freeDebug.\\n'\n"
                "    printf 'assembleFreeDebugAndroidTest - Assembles androidTest for freeDebug.\\n'\n"
                "    printf 'assembleFreeDebugUnitTest - Assembles unitTest for freeDebug.\\n'\n"
                "    printf 'assemblePaidDebug - Assembles main outputs for variant paidDebug.\\n'\n"
                "    printf 'connectedFreeDebugAndroidTest - Runs instrumented tests for freeDebug.\\n'\n"
                "    printf 'lintAnalyzeFreeDebug - Run lint analysis on freeDebug.\\n'\n"
                "    printf 'lintFixFreeDebug - Fix lint on freeDebug.\\n'\n"
                "    printf 'lintFreeDebug - Runs lint on freeDebug.\\n'\n"
                "    printf 'lintReportFreeDebug - Generate lint report on freeDebug.\\n'\n"
                "    printf 'testFreeDebugUnitTest - Run unit tests for freeDebug.\\n'\n"
                "    ;;\n"
                "esac\n"
                "exit 0\n",
                encoding="utf-8",
            )
            gradlew.chmod(0o644)

            quick = subprocess.run(
                ["bash", str(ANDROID_GRADLE_CHECK), "--quick", str(proj)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(quick.returncode, 0, msg=quick.stderr)
            self.assertEqual(gradlew.stat().st_mode & 0o777, 0o644)
            quick_calls = invocations_log.read_text(encoding="utf-8").splitlines()
            self.assertEqual(
                sum("tasks --all" in call for call in quick_calls),
                1,
                f"--quick must invoke 'tasks --all' at most once: {quick_calls}",
            )

            invocations_log.unlink()

            full = subprocess.run(
                ["bash", str(ANDROID_GRADLE_CHECK), "--full", str(proj)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(full.returncode, 0, msg=full.stderr)
            self.assertEqual(gradlew.stat().st_mode & 0o777, 0o644)
            full_calls = invocations_log.read_text(encoding="utf-8").splitlines()
            self.assertEqual(
                sum("tasks --all" in call for call in full_calls),
                1,
                f"--full must invoke 'tasks --all' at most once: {full_calls}",
            )
            self.assertIn("assembleFreeDebug --stacktrace", full_calls)
            self.assertIn("testFreeDebugUnitTest --stacktrace", full_calls)
            self.assertIn("lintFreeDebug --stacktrace", full_calls)
            self.assertNotIn("assembleDebug --stacktrace", full_calls)
            for call in full_calls:
                self.assertNotIn("lintFix", call)
                self.assertNotIn("lintAnalyze", call)
                self.assertNotIn("lintReport", call)


class SlangAndGitScriptTests(unittest.TestCase):
    """t-013: C-13b fixes for slang_compile_matrix.py and collect-git-context.sh."""

    def test_slang_compile_matrix_non_string_target_raises_manifest_error_and_exits_2(self) -> None:
        bad_manifest = {
            "source": "shaders/main.slang",
            "entries": [{"name": "vertexMain", "stage": "vertex"}],
            "targets": [["spirv"]],
        }
        with workspace_temp_dir() as temp_dir:
            manifest_path = temp_dir / "manifest.json"
            manifest_path.write_text(json.dumps(bad_manifest), encoding="utf-8")
            res = subprocess.run(
                [sys.executable, str(SLANG_MATRIX), "--print-only", str(manifest_path)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(res.returncode, 2, f"Expected exit 2, got {res.returncode}: {res.stderr}")
            self.assertNotIn("Traceback", res.stderr)
            self.assertNotIn("TypeError", res.stderr)

        mod = load_slang_module()
        manifest_error_cls = getattr(mod, "ManifestError", None)
        self.assertIsNotNone(manifest_error_cls, "slang_compile_matrix must define ManifestError")
        assert manifest_error_cls is not None
        with self.assertRaises(manifest_error_cls):
            mod.build_commands(bad_manifest)

    def test_slang_compile_matrix_non_string_stage_and_traversal_name_exit_2(self) -> None:
        mod = load_slang_module()
        invalid_cases = {
            "non_string_stage": {
                "source": "shaders/main.slang",
                "entries": [{"name": "vertexMain", "stage": ["vertex"]}],
            },
            "path_traversal_name": {
                "source": "shaders/main.slang",
                "entries": [{"name": "../escape", "stage": "vertex"}],
            },
        }
        for label, bad_manifest in invalid_cases.items():
            with self.subTest(case=label), workspace_temp_dir() as temp_dir:
                manifest_path = temp_dir / "manifest.json"
                manifest_path.write_text(json.dumps(bad_manifest), encoding="utf-8")
                res = subprocess.run(
                    [sys.executable, str(SLANG_MATRIX), "--print-only", str(manifest_path)],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(res.returncode, 2, f"{label}: expected exit 2, got {res.returncode}: {res.stderr}")
                self.assertNotIn("Traceback", res.stderr)
                self.assertNotIn("TypeError", res.stderr)
                with self.assertRaises(mod.ManifestError):
                    mod.build_commands(bad_manifest)

    def test_collect_git_context_uses_no_pager_on_git_log(self) -> None:
        script_text = COLLECT_GIT_CONTEXT.read_text(encoding="utf-8")
        log_lines = [
            line.strip()
            for line in script_text.splitlines()
            if not line.lstrip().startswith("#") and re.search(r"\bgit\b.*\blog\b", line)
        ]
        self.assertTrue(log_lines, "Expected at least one git log invocation in collect-git-context.sh")
        for line in log_lines:
            self.assertRegex(
                line,
                r"\bgit\s+--no-pager\s+log\b",
                f"git log invocation missing --no-pager: {line}",
            )

        with workspace_temp_dir() as repo_dir:
            env = {
                **os.environ,
                "GIT_AUTHOR_NAME": "Test",
                "GIT_AUTHOR_EMAIL": "test@example.com",
                "GIT_COMMITTER_NAME": "Test",
                "GIT_COMMITTER_EMAIL": "test@example.com",
                "GIT_PAGER": "false",
            }
            subprocess.run(["git", "init", "-q"], cwd=repo_dir, env=env, check=True)
            (repo_dir / "README.md").write_text("hello\n", encoding="utf-8")
            subprocess.run(["git", "add", "README.md"], cwd=repo_dir, env=env, check=True)
            subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=repo_dir, env=env, check=True)

            res = subprocess.run(
                ["sh", str(COLLECT_GIT_CONTEXT)],
                cwd=repo_dir,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(res.returncode, 0, msg=res.stderr)
            self.assertIn("== recent history ==", res.stdout)


if __name__ == "__main__":
    unittest.main()
