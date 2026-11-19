# Architecture and quality

## Project sanity checklist

Before adding feature code:

```bash
./gradlew assembleDebug
./gradlew lint
./gradlew test
```

If the project does not build, fix project structure first. Use [gradle-android-dev](../../gradle-android-dev/SKILL.md) for Gradle wrapper, `settings.gradle.kts`, version catalog, Android Gradle plugin, Kotlin plugin, `gradle.properties`, SDK levels, manifest merge, and module source sets.

## Module boundaries

- Domain models are plain Kotlin with business meaning — no DTO or database annotations; `core/domain` has no Android framework dependency.
- Repository interfaces live in domain; implementations live in data; UI state is neither a database entity nor a network DTO.
- Native handles and framework objects do not cross into domain — wrap them in lifecycle-safe abstractions; feature modules expose minimal public APIs.

## DI, coroutines, errors

- Use Hilt for Android-only projects; do not service-locate from Composables and do not inject `Activity` into long-lived classes; give native renderer wrappers explicit lifetimes.
- Use `viewModelScope` for screen work; never block main with `runBlocking`, `Thread.sleep`, bitmap decode, camera analysis, or native processing.
- Map low-level errors to user messages at the ViewModel/UI edge; preserve the original cause for logs and strip file paths, tokens, and user media metadata from them.

## Permissions and privacy

- Ask for runtime permissions only at the moment of need; prefer picker APIs over broad media permissions.
- Handle denial, one-time grants, and background restrictions.
- Keep EXIF location, face data, thumbnails, and cached media private; strip or preserve export metadata deliberately — never leak location in exported images.

## Data and background work

- Room for structured data, DataStore for settings, Paging 3 for large media grids.
- WorkManager for uploads, exports, and sync that must survive process death; declare foreground-service type and permissions explicitly for camera, location, or media projection.

## Testing

- Unit test use cases, repositories, mappers, and error mapping with fake data sources; map AGP test **tasks** (`testDebugUnitTest`, `connectedDebugAndroidTest`) via [gradle-android-dev](../../gradle-android-dev/SKILL.md); for camera/media/NDK boundaries use fake frame sources and test the Kotlin wrapper separately from native code.
- Test Android 16 behavior changes through emulator/device runs, not just compile checks.
