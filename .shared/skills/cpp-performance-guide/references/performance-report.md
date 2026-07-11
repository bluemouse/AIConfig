# Performance Report Template

Finish performance work with this compact report. Keep it precise enough for code review and future debugging.

```text
Goal:
- metric:
- target / budget:
- workload:
- platform:

Baseline:
- build:
- command(s):
- result:
- variance / confidence:

Bottleneck evidence:
- profiler / benchmark / counter source:
- observed hotspot or limiting factor:
- relevant excerpts:

Change(s):
- files changed:
- summary:
- why this should affect the bottleneck:

Correctness validation:
- tests run:
- sanitizer / race / numerical checks:
- result:

Performance result:
- command(s):
- before:
- after:
- delta:
- variance / confidence:

Tradeoffs and risks:
- correctness / numerical / threading / memory risks:
- maintainability cost:
- portability cost:

Conclusion:
- accepted improvement, inconclusive result, or regression:
- next best step:
```

If profiling or benchmarks could not be run, use this variant:

```text
Goal:
Static findings:
Why they are plausible bottlenecks:
Exact commands to validate:
Suggested minimal fix:
Risks:
Status: unmeasured hypothesis
```

Rules:

- Do not write "faster" without numbers.
- Do not omit failed experiments if they affect the recommended path.
- Include enough command detail for another agent or developer to reproduce the result.
