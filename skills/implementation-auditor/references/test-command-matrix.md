# Test Command Discovery

Choose verification commands from the repository, not from memory. Use repository-specific scripts, README instructions, and CI configuration before any generic command, and **report the source used to select commands**.

## Universal discovery

Inspect, in this order when present:

1. CI files: `.github/workflows/*`, `.gitlab-ci.yml`, `Jenkinsfile`, Azure Pipelines, Buildkite, TeamCity.
2. Build manifests: `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `build.gradle*`, `settings.gradle*`, `CMakeLists.txt`, `*.xcodeproj`, `*.xcworkspace`, `*.pro`, `pom.xml`, `Makefile`.
3. Project docs: `README*`, `CONTRIBUTING*`, `docs/*`, test directories.
4. Existing test names near changed files.

When a stack's command surface is not obvious from discovery (Xcode destinations, Android instrumented vs unit tasks, multiplatform Gradle test tasks), derive the invocation from the discovered CI or manifest evidence rather than guessing.

## Manual or environment-dependent validation

If the required platform cannot run locally, report the exact blocker and the closest evidence obtained — e.g. no Android device or emulator, no iOS simulator runtime, license/SDK/proprietary service unavailable, GPU/display server/hardware sensor required. Do not convert blocked validation into a pass.
