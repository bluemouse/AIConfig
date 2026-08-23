# Test Command Matrix

Use repository-specific scripts, README instructions, and CI configuration before these generic commands. Replace placeholders such as scheme, module, device, preset, target, and test pattern with values discovered from the repo.

## Universal discovery

Inspect, in this order when present:

1. CI files: `.github/workflows/*`, `.gitlab-ci.yml`, `Jenkinsfile`, Azure Pipelines, Buildkite, TeamCity.
2. Build manifests: `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `build.gradle*`, `settings.gradle*`, `CMakeLists.txt`, `*.xcodeproj`, `*.xcworkspace`, `*.pro`, `pom.xml`, `Makefile`.
3. Project docs: `README*`, `CONTRIBUTING*`, `docs/*`, test directories.
4. Existing test names near changed files.

Always report the source used to select commands.

## Android

### Kotlin / Java with Gradle

Focused local unit tests:

```bash
./gradlew :<module>:testDebugUnitTest --tests '<package.ClassTest.testName>'
```

Module unit tests:

```bash
./gradlew :<module>:testDebugUnitTest
```

Instrumentation tests when UI, Android framework, database, lifecycle, or device behavior changed:

```bash
./gradlew :<module>:connectedDebugAndroidTest
```

Static/build checks commonly used by Android projects:

```bash
./gradlew :<module>:assembleDebug
./gradlew :<module>:lintDebug
```

### Native Android / NDK C++

```bash
./gradlew :<module>:externalNativeBuildDebug
./gradlew :<module>:connectedDebugAndroidTest
```

Use emulator/device evidence for JNI, graphics, sensor, lifecycle, or platform API changes.

## iOS / macOS Apple platforms

### Swift / Objective-C with Xcode

List schemes and destinations if unknown:

```bash
xcodebuild -list
xcodebuild -showdestinations -scheme <Scheme>
```

Focused or suite tests:

```bash
xcodebuild test -scheme <Scheme> -destination 'platform=iOS Simulator,name=<Device>,OS=<OS>' -only-testing:<TestBundle>/<TestClass>/<testMethod>
xcodebuild test -scheme <Scheme> -destination 'platform=iOS Simulator,name=<Device>,OS=<OS>'
```

Build-only validation:

```bash
xcodebuild build -scheme <Scheme> -destination 'generic/platform=iOS Simulator'
```

Use macOS destinations for desktop app, framework, or command-line targets.

## Desktop C++

### CMake / Ninja / Make

Configure and build:

```bash
cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug
cmake --build build --target <target> -j
```

CTest focused and full:

```bash
ctest --test-dir build -R '<test_regex>' --output-on-failure
ctest --test-dir build --output-on-failure
```

GoogleTest executable focused:

```bash
./build/<path>/<test_binary> --gtest_filter=<Suite.Test>
```

Use sanitizer builds when changes touch memory ownership, threading, parsing, graphics buffers, or unsafe C APIs.

### Bazel C++

```bash
bazel test //path/to:target --test_filter=<Suite.Test>
bazel test //...
```

## Qt desktop

### Qt with CMake

```bash
cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug
cmake --build build --target <test_target> -j
ctest --test-dir build -R '<qt_test_name>' --output-on-failure
```

Direct Qt test executable:

```bash
./build/<test_binary> -v2
```

For GUI behavior, report whether the environment supports display, offscreen platform, or a real desktop session:

```bash
QT_QPA_PLATFORM=offscreen ctest --test-dir build -R '<test_regex>' --output-on-failure
```

### Qt with qmake

```bash
qmake
make -j
./<test_binary> -v2
```

## Kotlin non-Android

### Gradle JVM / Multiplatform

```bash
./gradlew test --tests '<package.ClassTest.testName>'
./gradlew test
./gradlew check
```

For multiplatform modules:

```bash
./gradlew :<module>:jvmTest
./gradlew :<module>:iosSimulatorArm64Test
./gradlew :<module>:allTests
```

## Java / JVM

### Gradle

```bash
./gradlew test --tests '<package.ClassTest.testName>'
./gradlew check
```

### Maven

```bash
mvn -Dtest=<ClassName>#<methodName> test
mvn test
mvn verify
```

## JavaScript / TypeScript

```bash
npm test -- <test_pattern>
npm run test
npm run typecheck
npm run lint
```

Use the project’s package manager when lockfiles indicate it: `pnpm`, `yarn`, or `bun`.

## Python

```bash
pytest path/to/test_file.py::test_name -q
pytest -q
python -m pytest -q
```

Add type/static checks if configured:

```bash
mypy .
ruff check .
```

## Rust

```bash
cargo test <test_name>
cargo test
cargo clippy --all-targets --all-features
```

## Go

```bash
go test ./path/to/package -run TestName
go test ./...
go test -race ./...
```

Use `-race` for concurrency, shared state, lifecycle, or cancellation changes when practical.

## Manual or environment-dependent validation

If the required platform cannot run locally, report the exact blocker and the closest evidence obtained. Examples:

- No Android device or emulator available.
- No iOS simulator runtime installed.
- License, SDK, or proprietary service unavailable.
- GPU, display server, hardware sensor, or network service required.

Do not convert blocked validation into a pass.
