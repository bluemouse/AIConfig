# Testing, debugging, and validation workflow

Use this reference when implementing tests, diagnosing failures, or proving a Python CLI script is ready.

## Test strategy

Test the core logic separately from the CLI boundary:

- Pure functions: simple unit tests with explicit inputs and outputs.
- Parsers: direct tests of `parse_args([...])`.
- CLI main: call `main([...])` and assert exit codes and captured output.
- Filesystem behavior: use `tmp_path` in pytest or `tempfile.TemporaryDirectory` in unittest.
- Subprocess behavior: wrap subprocess calls and mock the wrapper, not `subprocess.run` everywhere.
- Error cases: invalid arguments, missing files, malformed JSON/CSV/TOML, permission errors, partial records, and external command failures.

## pytest patterns

```python
def test_main_success(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    input_path = tmp_path / "input.txt"
    input_path.write_text("hello\n", encoding="utf-8")

    status = main([str(input_path)])

    assert status == 0
    assert capsys.readouterr().out == "hello\n"
```

Use fixtures for shared setup, but avoid over-abstracting tests until duplication is painful.

## unittest pattern

Use when no third-party dependencies are allowed:

```python
class TestCore(unittest.TestCase):
    def test_transform(self) -> None:
        self.assertEqual(transform("a"), "A")
```

Run with:

```bash
python -m unittest discover -s tests
```

## Golden files

Use golden files only for stable, meaningful text output. When using them:

- Keep them small and readable.
- Normalize platform-specific paths and line endings.
- Provide an intentional update workflow.
- Avoid giant snapshots that hide important diffs.

## Property-based testing

Use Hypothesis when input space is broad and invariants are clear, for example parsers, serializers, path normalization, idempotent transforms, sorting, and round-trips.

Example invariants:

- `parse(format(x)) == x` for supported values.
- Running a normalization twice gives the same result.
- Output ordering is deterministic.
- Invalid input never crashes with an unrelated exception.

## Debugging workflow

1. Reproduce with the smallest command, input, and environment.
2. Add or run a failing test that captures the bug.
3. Inspect boundaries first: argv parsing, paths, encodings, current working directory, environment variables, and dependency versions.
4. Use `logging` or `breakpoint()` to inspect state.
5. Fix the root cause, not only the symptom.
6. Keep the regression test.

## Common debugging commands

```bash
python --version
python -X dev script.py args...
python -W error script.py args...
python -m pdb script.py args...
python -m trace --trace script.py args...
python -m compileall -q .
```

Use `-X dev` to enable additional runtime checks during development when relevant.

## Handling flaky behavior

Typical causes:

- Dependence on wall-clock time, locale, current directory, environment, filesystem ordering, random seed, network, or external command versions.
- Tests sharing mutable global state or temp paths.
- Async tasks not awaited or cleaned up.

Mitigations:

- Inject clocks, random generators, and external adapters.
- Sort filesystem listings before deterministic output.
- Use temporary directories per test.
- Reset environment changes with fixtures or context managers.

## Performance validation

Do not optimize blindly. Establish:

- Input size and growth expectations.
- Time and memory target.
- Current bottleneck.
- Algorithmic complexity.

Basic workflow:

```bash
python -m timeit -s 'from module import func' 'func(data)'
python -m cProfile -o profile.out script.py args...
python -m pstats profile.out
```

Optimize in this order:

1. Avoid unnecessary work.
2. Use better algorithms or data structures.
3. Stream instead of loading everything.
4. Use builtins and standard library tools implemented in C.
5. Cache repeated expensive pure computations.
6. Consider concurrency only after knowing the bottleneck.

## Completion gate

Before delivering code, run or recommend the closest possible gate:

```bash
python -m compileall -q src tests
python -m ruff format --check .
python -m ruff check .
python -m pyright
python -m pytest -q
```

For single-file standard-library scripts:

```bash
python -m py_compile script.py
python script.py --help
python -m unittest discover -s tests
```

When a command was not run, say so plainly and give the exact command the user should run.
