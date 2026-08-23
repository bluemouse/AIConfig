# UI, camera, media, painting, and photography

## Use this file when

Use this reference for Jetpack Compose UI, camera preview/capture, media playback, photo picking, painting canvases, image editing, and photography user flows.

## Edge-to-edge and Android 16 insets

Apps targeting Android 16/API 36 cannot opt out of edge-to-edge. Handle insets explicitly — do not rely on `windowOptOutEdgeToEdgeEnforcement`.

In `Activity.onCreate()`:

```kotlin
override fun onCreate(savedInstanceState: Bundle?) {
    enableEdgeToEdge()
    super.onCreate(savedInstanceState)
    // ...
}
```

In Compose, apply safe insets on interactive content:

```kotlin
Scaffold(
    modifier = Modifier.fillMaxSize(),
    contentWindowInsets = WindowInsets.safeDrawing
) { innerPadding ->
    EditorScreen(
        modifier = Modifier
            .fillMaxSize()
            .padding(innerPadding),
        // ...
    )
}
```

Rules:

- Use `WindowInsets.safeDrawing`, `navigationBarsPadding()`, or scaffold `innerPadding` — not `fitsSystemWindows` as a global fix.
- Set `android:windowSoftInputMode="adjustResize"` when the keyboard should resize content.
- Test on 3-button and gesture navigation; status and navigation bars overlay content.

## Predictive back

For apps targeting Android 16/API 36:

- Do not depend on `onBackPressed()` or `KeyEvent.KEYCODE_BACK`.
- Use `OnBackInvokedCallback` for custom back behavior, or Navigation Compose back stack with predictive animations enabled.
- Test back from camera preview, modal sheets, and export flows.

## Compose screen structure

Recommended screen shape:

```kotlin
@Composable
fun EditorRoute(
    viewModel: EditorViewModel = hiltViewModel(),
    onBack: () -> Unit
) {
    val state by viewModel.uiState.collectAsStateWithLifecycle()
    EditorScreen(
        state = state,
        onAction = viewModel::onAction,
        onBack = onBack
    )
}

@Composable
private fun EditorScreen(
    state: EditorUiState,
    onAction: (EditorAction) -> Unit,
    onBack: () -> Unit
) {
    // Stateless UI. Previewable. No repository, decoder, player, or native call here.
}
```

Rules:

- Keep side effects in `LaunchedEffect` or `DisposableEffect`, not inline in composable body.
- Use `rememberUpdatedState` for callbacks captured by effects.
- Use `rememberSaveable` for selected tab/tool/brush properties that should survive recreation.
- Use stable keys for media grids and lazy lists.
- Avoid allocating bitmaps, decoders, players, cameras, or native renderers during recomposition.
- Use `Modifier.semantics`, content descriptions, large touch targets, and keyboard support.

## Camera API choice

Use CameraX by default:

- Standard preview/capture/video/image analysis.
- Lifecycle-aware preview binding.
- Device compatibility across many OEMs.
- ImageAnalysis backpressure and analyzer abstractions.

Use Camera2 when the feature needs:

- Manual exposure/focus/ISO/shutter controls beyond CameraX support.
- Custom stream combinations or low-level session control.
- Precise frame timing, reprocessing, RAW details, or vendor capability checks.

Use NDK/native camera APIs only when the app has a measured need for native processing or low-level interop. Use `android-ndk-dev` for that bridge.

## CameraX preview in Compose

Prefer a platform preview view hosted by Compose rather than implementing preview drawing from scratch.

```kotlin
@Composable
fun CameraPreview(
    controller: LifecycleCameraController,
    modifier: Modifier = Modifier
) {
    AndroidView(
        modifier = modifier,
        factory = { context ->
            PreviewView(context).apply {
                this.controller = controller
                scaleType = PreviewView.ScaleType.FILL_CENTER
            }
        }
    )
}
```

Rules:

- Bind camera to lifecycle and release it when the lifecycle ends.
- Do not start camera before permission is granted.
- Handle unavailable camera, concurrent camera restrictions, rotation, display cutouts, and foldable states.
- Keep camera control state in ViewModel or an explicit controller class, not in Composables.

## Image analysis and photo processing

- Set an explicit analyzer backpressure strategy.
- Close every frame (`ImageProxy.close()`) even on error.
- Avoid converting every preview frame to `Bitmap`; stay in YUV when possible.
- Process only the resolution needed for the current UI/algorithm.
- Use a bounded queue or drop policy for real-time preview filters.
- Use `Dispatchers.Default`, a native worker, or Vulkan compute for heavy filters.
- Keep orientation, crop rect, sensor rotation, and color space metadata attached to frames.

## Photo picker, MediaStore, and storage

- Use Android Photo Picker for user-selected photos/videos when broad library access is unnecessary.
- Use app-private storage for drafts, caches, and intermediate layers.
- Use MediaStore for exported images/videos that should appear in the user's media library.
- Preserve EXIF only when product requirements say so. Strip location by default when exporting shared images unless the user opts in.
- Decode large images with target dimensions and a memory budget.

## Media playback and editing

- Use Media3 for playback UI, background playback, track selection, and common player workflows.
- Keep player instances lifecycle-aware. Release them in `onStop` or `DisposableEffect` when appropriate.
- Use lower-level codecs or NDK APIs only for custom decode/encode/transcode pipelines. See `android-ndk-dev`.
- For media plus Vulkan rendering, hand off frame interop and GPU processing to `android-vulkan-dev`.

## Painting app defaults

Use Compose Canvas when:

- The canvas is small or moderate.
- Brush count is low.
- Latency requirements are normal UI latency.
- Export is not too large.

Use tiled CPU/native/Vulkan rendering when:

- Canvas can exceed device texture or memory limits.
- Brush strokes are high frequency and must feel under 16 ms/frame.
- Layers, masks, blend modes, and filters are non-destructive.
- The app needs real-time camera/image filters or large photo edits.

Painting state guidelines:

- Store strokes as vector commands plus raster caches, not only one mutable bitmap.
- Use tiles or layers to avoid redrawing the whole image every stroke.
- Keep undo/redo incremental and bounded by memory budget.
- Export from a background worker and report progress.
- Separate UI tool state from document model state.

## Accessibility and adaptive UI

- Minimum touch target is 48 dp; prefer larger for camera shutter, brush controls, and destructive actions.
- Do not rely on color alone for histogram, selection, warnings, or focus states.
- Support landscape, large screens, foldables, keyboard, and stylus where relevant.
- Ensure edge-to-edge content avoids system bars and cutouts.
- Provide meaningful labels for capture, edit, export, undo, redo, and tool controls.

## Common anti-patterns

- Starting camera or player inside a recomposing function.
- Blocking main with decode/filter/export work.
- Keeping full-resolution images in Compose state.
- Recreating `ImageBitmap`, shader, player, or preview session every recomposition.
- Dropping orientation/color metadata during edits.
- Asking for broad media permissions when picker or MediaStore is enough.
- Using CPU per-pixel Kotlin loops for real-time preview filters that should be native or GPU.
