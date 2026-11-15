# Architecture and quality

## Use this file when

Use this reference when designing modules, app state, data flow, dependency injection, error handling, permissions, tests, or code review criteria for a Kotlin Android app.

## Project sanity checklist

Before adding feature code:

```bash
./gradlew assembleDebug
./gradlew lint
./gradlew test
```

If the project does not build, fix project structure first. Use [gradle-android-dev](../../gradle-android-dev/SKILL.md) for Gradle wrapper, `settings.gradle.kts`, version catalog, Android Gradle plugin, Kotlin plugin, `gradle.properties`, SDK levels, manifest merge, and module source sets.

## Recommended module boundaries

Small apps can use `app`, `core`, and `feature/*`. Larger apps should split by stable boundaries, not by every screen.

```text
app -> feature/*, core/ui, core/data, core/domain
feature/* -> core/ui, core/domain
core/data -> core/domain
core/domain -> no Android framework dependency
core/nativebridge -> Kotlin wrappers over native libraries, called by data/domain use cases
```

Rules:

- Domain models are plain Kotlin and contain business meaning, not DTO or database annotations.
- Repository interfaces live in domain. Implementations live in data.
- UI state is not a database entity and not a network DTO.
- Native handles and framework objects do not cross into domain. Wrap them in lifecycle-safe abstractions.
- Feature modules expose minimal public APIs: navigation entry, DI bindings, and test fixtures.

## Use case and repository pattern

Use use cases for meaningful operations, not for every one-line getter.

```kotlin
class ApplyPresetUseCase(
    private val imageRepository: ImageRepository,
    private val rendererRepository: RendererRepository
) {
    suspend operator fun invoke(photoId: PhotoId, preset: PresetId): Result<EditedPhoto> {
        val source = imageRepository.loadOriginal(photoId).getOrElse { return Result.failure(it) }
        return rendererRepository.applyPreset(source, preset)
    }
}
```

Repository implementation pattern:

- Coordinate local cache, remote APIs, MediaStore, and optional native pipelines.
- Map DTO/entity/native output to domain objects before returning.
- Expose `Flow` for observable local state.
- Keep transaction and threading decisions inside repository/data source methods.

## ViewModel and UI state

A ViewModel should orchestrate UI work and delegate business logic.

```kotlin
sealed interface SaveStatus {
    data object Idle : SaveStatus
    data object Saving : SaveStatus
    data class Failed(val message: String) : SaveStatus
    data class Saved(val uri: Uri) : SaveStatus
}

data class ExportUiState(
    val status: SaveStatus = SaveStatus.Idle,
    val progress: Float = 0f
)
```

Rules:

- Expose immutable `StateFlow` or Compose state; keep mutable state private.
- Keep business logic out of Composables.
- Keep serialization, database, bitmap decode, media IO, and native calls out of Composables.
- Map domain errors to user messages at the ViewModel/UI edge.

## Coroutine rules

- Use `viewModelScope` for screen work, `lifecycleScope` for lifecycle-owned UI work, and application scope only for app-wide jobs with explicit ownership.
- Use `Dispatchers.IO` for file/database/network/media IO.
- Use `Dispatchers.Default` for CPU work such as parsing, resizing, CPU image filters, and ML preprocessing.
- Never block main with `runBlocking`, `Thread.sleep`, bitmap decode, camera analysis, or native processing.
- Prefer `supervisorScope` for independent child work where one failure should not cancel siblings.
- Always handle cancellation and close camera/media/image resources in `finally` or with `use`-style helpers.

## Dependency injection

Use Hilt for Android-only projects unless the user has another standard. Keep bindings near module boundaries.

```kotlin
@Module
@InstallIn(SingletonComponent::class)
abstract class RepositoryModule {
    @Binds
    abstract fun bindImageRepository(impl: ImageRepositoryImpl): ImageRepository
}
```

Rules:

- Inject repositories/use cases into ViewModels.
- Do not service-locate from Composables.
- Do not inject `Activity` into long-lived classes.
- Give native renderer wrappers explicit lifetimes; do not make a GPU context a singleton unless the app is designed around a single renderer.

## Error handling

Use `Result` for simple local failures or a custom sealed error type for user-visible flows.

```kotlin
sealed interface AppError {
    data object PermissionDenied : AppError
    data object UnsupportedDevice : AppError
    data class DecodeFailed(val cause: Throwable) : AppError
    data class NativeFailure(val code: Int, val detail: String) : AppError
}
```

Rules:

- Preserve the original cause for logs and crash reports.
- Convert low-level errors to useful user messages at the UI boundary.
- Do not retry camera/media/native failures indefinitely.
- Log enough context for debugging, but strip file paths, tokens, and user media metadata when unnecessary.

## Permissions and privacy

- Ask for runtime permissions only at the moment of need.
- Prefer picker APIs over broad media permissions for user-selected photos/videos.
- Explain camera/microphone access before prompting when the product flow benefits from context.
- Handle denial, one-time grants, and background restrictions.
- Keep EXIF location, face data, thumbnails, and cached media private unless the user explicitly exports or shares them.
- For photography apps, preserve or strip metadata deliberately; do not accidentally leak location in exported images.

## Testing strategy

- Unit test use cases, repositories, mappers, and error mapping with fake data sources.
- Use [kotlin-testing](../../kotlin-testing/SKILL.md) for test design, Kotest/MockK, coroutine tests, and flaky-test triage.
- Use Robolectric or instrumentation only when Android framework behavior matters. Map Android Gradle test **tasks** (`testDebugUnitTest`, `connectedDebugAndroidTest`) via [gradle-android-dev](../../gradle-android-dev/SKILL.md).
- Test Compose screens with stable semantics, not pixel-perfect snapshots only.
- For camera/media, provide fake frame sources and fake media repositories for deterministic tests.
- For NDK/Vulkan boundaries, unit test the Kotlin wrapper separately from native implementation, and use integration tests on real devices for performance paths.
- Test Android 16 behavior changes through emulator/device runs, not just compile checks.

## Data and background work pointers

- **Local persistence:** Room for structured data; DataStore (Preferences or Proto) for settings and small typed state.
- **Paged lists:** Paging 3 for large media grids or feeds.
- **Deferrable work:** WorkManager for uploads, exports, and sync that must survive process death.
- **Foreground services:** declare type and permissions explicitly when camera capture, location, or media projection requires a visible ongoing task.

## Code review checklist for junior developers

- The feature has a clear owner layer: UI, domain, data, native bridge, or renderer.
- Public APIs use domain types or stable wrapper types.
- No `!!` or uncaught nullable server/media metadata assumptions.
- Main thread is never blocked.
- Every `Closeable`, image, camera session, player, sensor, native handle, or renderer has a release path.
- UI state is immutable and survives configuration changes where required.
- Permissions and denied states are handled.
- Large image/media work has a memory budget.
- The feature builds, passes lint/tests, and has manual test notes for device-specific camera/media behavior.
