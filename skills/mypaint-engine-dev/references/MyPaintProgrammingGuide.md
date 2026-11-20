---
title: "MyPaint and libmypaint Deep Implementation Reference"
summary: "Extended numerical, schema, and shader reference complementing architecture.md, brush-engine.md, surface-layer-gpu.md, performance-validation.md, and source-map.md."
last_updated: "2026-07-06"
libmypaint_reference_version: "upstream master (unified mypaint_brush_stroke_to API; mypaint repo may bundle 1.6.x)"
---

# MyPaint and libmypaint Deep Implementation Reference

Read the focused references first (`architecture.md`, `brush-engine.md`, `surface-layer-gpu.md`, `performance-validation.md`, `source-map.md`). Load this document for contributor build/startup specifics, the complete `.myb` 63-setting / 18-input catalog, exact parity formulas not expanded in the focused summaries, 10-band spectral constants, RNG/Gaussian constants, and reference SkSL/GLSL GPU kernels.

---

## 1. MyPaint App Build, Startup, and Bridge Details

High-level MVC ownership, stroke routing, and extension seams live in [architecture.md](architecture.md). Keep these implementation-specific constraints when modifying the Python/GTK host or C++ bridge:

- **Build & local test commands (`BUILDING.md`):**
  - `python setup.py demo` — run from checkout without installing.
  - `python setup.py nosetests` — doctests and lightweight Python suites.
  - `python setup.py test` — full Python + C++/libmypaint extension suite.
  - `python setup.py clean --all` — purge stale extension artifacts.
  - `setup.py` links against the `libmypaint` resolved by `pkg-config`, **not** a vendored `libmypaint-1.6.1/` tree, unless you install your local build and set `PKG_CONFIG_PATH` + `build_ext --set-rpath`.
- **Import-order hazard (`mypaint.py` → `gui/main.py` → `gui/application.py`):** `gui.main.main()` must apply GTK workarounds, cache GLib user dirs (`lib.glib.init_user_dir_caches()`), and initialize gettext (`lib.gettext_setup.init_gettext()`) **before** importing `gui.application` or `lib.mypaintlib` (`gui/resources.xml`, `gui/mypaint.glade`), otherwise GLib user-dir lookup and GTK icon/theme loading break on some platforms.
- **Pending brushwork flush:** before save, export, or ORA serialization (which also persists document-specific JSON settings), call `lib.document.Document.sync_pending_changes()` so active `BrushworkModeMixin` / `lib.command.Brushwork` recorders commit pending strokes into `CommandStack`. Stroke return values drive `split_due` command segmentation.
- **View mirror vs native symmetry angle:**
  - Viewport mirroring stays in `gui.document.Document`: `mirror_horizontal_cb()` calls `TiledDrawWidget.mirror()`; `mirror_vertical_cb()` rotates the view by `pi` and mirrors it (no libmypaint state change).
  - Model-space symmetry flows from `RootLayerStack` (`gui/resources.xml` `SymmetryActive`, `gui.symmetry.SymmetryEditMode` / `SymmetryEditOptionsWidget` / `SymmetryOverlay`) via `_propagate_symmetry_state()` → `lib/tiledsurface.hpp::TiledSurface::set_symmetry_state()` → `mypaint_tiled_surface_set_symmetry_state()`. The C++ bridge currently passes `symmetry_angle = 0.0` even though native libmypaint supports arbitrary symmetry axis angles; `mypaint_tiled_surface_begin_atomic()` refreshes matrices via `mypaint_update_symmetry_state()`, and `draw_dab_internal()` transforms dab centers/angles with `mypaint_transform_point()` (e.g. vertical `symm_x = 2 * center_x - x`, `angle = -angle`).

---

## 2. Complete `.myb` v3 Settings and Dynamic Inputs Catalog

Preset JSON structure (`version: 3`, `settings` map, 0 or 2..64 non-decreasing control points per input curve, slope extrapolation) is specified in [brush-engine.md](brush-engine.md) §§2–3. Note that setting base values through `mypaint_brush_from_string` / official setters is required because setters refresh cached derived coefficients (such as speed-remap `m`/`q`). Top-level keys like `comment`, `group`, `parent_brush_name`, and setting `restore_color` are host/UI metadata ignored by brush simulation.

### 2.1 All 63 Brush Settings (`libmypaint` 1.6.x / master)

| Setting ID | Default | Role / Units |
| --- | --- | --- |
| `opaque` | `1.0` | Base paint opacity (`0..1`) |
| `opaque_multiply` | `0.0` | Multiplier combined with `opaque` (typically pressure-mapped) |
| `opaque_linearize` | `0.9` | Perceptual overlap linearization factor (read from base value) |
| `radius_logarithmic` | `2.0` | Brush radius in log space (`px = exp(value)`, `exp(2.0) ≈ 7.39` px) |
| `hardness` | `0.8` | Dab falloff knee (`0` = soft, `1` = hard stamp) |
| `anti_aliasing` | `1.0` | Minimum fadeout width (px) enforced via geometric reparameterization |
| `dabs_per_basic_radius` | `0.0` | Dabs emitted per `exp(base(radius_logarithmic))` travel |
| `dabs_per_actual_radius` | `2.0` | Dabs emitted per current dynamic radius travel |
| `dabs_per_second` | `0.0` | Time-based dab emission rate (Hz) |
| `radius_by_random` | `0.0` | Gaussian noise amplitude in log-radius space |
| `speed1_slowness` | `0.04` | EMA smoothing constant for fine speed (`speed1`) |
| `speed2_slowness` | `0.8` | EMA smoothing constant for gross speed (`speed2`) |
| `speed1_gamma` | `4.0` | Log-remap gamma for `speed1` (`gamma = exp(base_value)`) |
| `speed2_gamma` | `4.0` | Log-remap gamma for `speed2` (`gamma = exp(base_value)`) |
| `offset_by_random` | `0.0` | Gaussian position jitter in base-radius units |
| `offset_by_speed` | `0.0` | Offset along smoothed motion vector (`* 0.1 / viewzoom`) |
| `offset_by_speed_slowness` | `1.0` | Smoothing for speed-offset vector (`norm_dx_slow`, `norm_dy_slow`) |
| `slow_tracking` | `0.0` | Event-rate virtual-cursor position stabilizer |
| `slow_tracking_per_dab` | `0.0` | Per-dab position stabilizer strength |
| `tracking_noise` | `0.0` | Gaussian cursor tremor before slow tracking |
| `color_h` | `0.0` | Base HSV hue (`0..1` turns; overwritten by host active color) |
| `color_s` | `0.0` | Base HSV saturation (`0..1`) |
| `color_v` | `0.0` | Base HSV value (`0..1`) |
| `restore_color` | `0.0` | Host-UI hint to keep preset `color_h/s/v` on selection |
| `change_color_h` | `0.0` | Per-dab HSV hue shift (cyclic turns) |
| `change_color_l` | `0.0` | Per-dab HSL lightness shift |
| `change_color_hsl_s` | `0.0` | Per-dab headroom-scaled HSL saturation shift |
| `change_color_v` | `0.0` | Per-dab HSV value shift |
| `change_color_hsv_s` | `0.0` | Per-dab `s*v`-scaled HSV saturation shift |
| `smudge` | `0.0` | Wet mix factor from smudge bucket (`0..1`) |
| `smudge_length` | `0.5` | Sample retention factor before re-pickup |
| `smudge_radius_log` | `0.0` | Log multiplier on dab radius for `get_color` pickup |
| `smudge_length_log` | `0.0` | Non-linear exponent on resample threshold |
| `smudge_bucket` | `0.0` | Smudge state slot (`round` clamped to `0..n-1`, max `255`) |
| `smudge_transparency` | `0.0` | Sampled-alpha gate aborting dab draw (sign inverts sense) |
| `eraser` | `0.0` | Scales `eraser_target_alpha` by `(1 - eraser)` |
| `stroke_threshold` | `0.0` | Pressure threshold to start `stroke` progression |
| `stroke_duration_logarithmic` | `4.0` | Progression rate of `stroke` input |
| `stroke_holdtime` | `0.0` | Hold duration at `stroke = 1.0` before reset |
| `custom_input` | `0.0` | Target value for stateful `custom` channel |
| `custom_input_slowness` | `0.0` | EMA smoothing toward `custom_input` |
| `elliptical_dab_ratio` | `1.0` | Dab ellipse aspect ratio (`>= 1.0`, `1` = circle) |
| `elliptical_dab_angle` | `90.0` | Dab ellipse rotation angle (degrees) |
| `direction_filter` | `2.0` | Smoothing constant for `direction` channel |
| `lock_alpha` | `0.0` | Lock-alpha blend weight (`0..1`) |
| `colorize` | `0.0` | Colorize (hue/chroma over dst luma) blend weight (`0..1`) |
| `snap_to_pixel` | `0.0` | Interpolate center to `n + 0.5` and radius to `0.5` steps |
| `pressure_gain_log` | `0.0` | Non-linear pressure gain applied once at input stage |
| `gridmap_scale` | `0.0` | Global log scale for 256-px `gridmap_x`/`gridmap_y` |
| `gridmap_scale_x` | `1.0` | X-axis scale multiplier for `gridmap_x` |
| `gridmap_scale_y` | `1.0` | Y-axis scale multiplier for `gridmap_y` |
| `offset_x` | `0.0` | Canvas-space X offset (scaled by `exp(offset_multiplier) * base_radius`) |
| `offset_y` | `0.0` | Canvas-space Y offset |
| `offset_angle` | `0.0` | `FLIP`-alternated offset relative to motion direction |
| `offset_angle_asc` | `0.0` | `FLIP`-alternated offset relative to `tilt_ascension` |
| `offset_angle_view` | `0.0` | `FLIP`-alternated offset relative to view rotation |
| `offset_angle_2` | `0.0` | Non-flipped second offset relative to motion direction |
| `offset_angle_2_asc` | `0.0` | Non-flipped second offset relative to `tilt_ascension` |
| `offset_angle_2_view` | `0.0` | Non-flipped second offset relative to view rotation |
| `offset_angle_adj` | `0.0` | Reference-angle offset added to `offset_angle*` terms |
| `offset_multiplier` | `0.0` | Log scale (`exp(offset_multiplier)`) applied to directional offsets |
| `posterize` | `0.0` | Posterize blend weight (`0..1`, preserves alpha) |
| `posterize_num` | `0.05` | Quantization levels (`ROUND(posterize_num * 100)` clamped `1..128`) |
| `paint_mode` | `0.0` (`1.6.x`; `1.0` master) | Pigment mix (`0` = additive RGB, `1` = 10-band spectral WGM) |

*(Note: 63 setting keys in `libmypaint` 1.6.x `brushsettings.json`; spectral-default upstream master sets `paint_mode` default to `1.0` and adds `softness` with default `0.0`.)*

### 2.2 All 18 Dynamic Mapping Inputs

| Input ID | Typical Range | Derivation & Statefulness |
| --- | --- | --- |
| `pressure` | `0..1` | Clamped `>= 0`, transformed once by `pressure_gain_log` |
| `speed1` | `~0..4` | Stateful EMA fine speed (`* viewzoom`), log-remapped (§3.2) |
| `speed2` | `~0..4` | Stateful EMA gross speed (`* viewzoom`), log-remapped (§3.2) |
| `random` | `0..1` | Uniform value from Knuth LFIB RNG; advances **once per emitted dab** |
| `stroke` | `0..1` | Stateful stroke progress gated by `stroke_threshold` / `stroke_holdtime` |
| `direction` | `0..180` | Stateful filtered motion angle, 180°-periodic |
| `direction_angle` | `0..360` | Stateful filtered motion angle, full 360° |
| `tilt_declination` | `0..90` | `90 - hypot(xtilt, ytilt) * 60` (`90°` when upright) |
| `tilt_ascension` | `-180..180` | `degrees(atan2(-xtilt, ytilt))` (shortest-angle interpolated) |
| `tilt_declinationx` | `-90..90` | `xtilt * 60` (`xtilt` clamped `-1..1`) |
| `tilt_declinationy` | `-90..90` | `ytilt * 60` (`ytilt` clamped `-1..1`) |
| `attack_angle` | `-180..180` | Smallest signed angle between `tilt_ascension` and stroke direction (`+90°` frame) |
| `barrel_rotation` | `-180..180` | Stylus barrel twist (turns → degrees, shortest-angle interpolated) |
| `viewzoom` | log | Logarithmic view zoom adjustment in radius space |
| `brush_radius` | log | Base `radius_logarithmic` setting value (`BASEVAL(RADIUS_LOGARITHMIC)`) |
| `gridmap_x` | `0..256` | `v = fmodf(|x * gridmap_scale_x|, expf(gridmap_scale) * 256.0f) / expf(gridmap_scale)`, mirrored as `256.0f - v` when `x * gridmap_scale_x < 0` |
| `gridmap_y` | `0..256` | `v = fmodf(|y * gridmap_scale_y|, expf(gridmap_scale) * 256.0f) / expf(gridmap_scale)`, mirrored as `256.0f - v` when `y * gridmap_scale_y < 0` |
| `custom` | varies | Stateful EMA smoothing toward `custom_input` |

---

## 3. Parity-Critical Brush Core Math

Core scheduler structure and per-dab order live in [brush-engine.md](brush-engine.md) §§4–7. Exact formulas required for numerical parity with `mypaint-brush.c`:

### 3.1 Input Sanitization & Step Ordering

- Clamp `xtilt, ytilt` to `[-1, 1]`, `pressure <= 0` to `0`, `dt <= 0` to `0.0001`.
- Treat `dt > 5.0` or non-finite coordinates as a stroke reset boundary (force `x/y` and dynamic view inputs to `0` for that call; emit no dabs).
- Scale velocity deltas by `viewzoom` before updating `speed1`/`speed2` so speed curves respond to screen-space motion.
- **Mandatory per-dab evaluation order:** (a) interpolate `(x, y, pressure, tilt, barrel_rotation)` to dab fraction; (b) read derived inputs (`speed1/2`, `direction`) from **current** pre-step state; (c) evaluate all setting mappings; (d) integrate stateful channels (`speed1/2`, `direction`, `custom`, `stroke`) for the **next** step. Reordering (b)/(c)/(d) shifts dynamic response.

### 3.2 Logarithmic Speed Remap (`speed1`, `speed2`)

Precomputed whenever `base_value(speed1_gamma)` or `base_value(speed2_gamma)` changes (never from dynamic mapped values):

```text
gamma  = exp(base_speed_gamma)
fix1_x = 45.0,  fix1_y  = 0.5
fix2_x = 45.0,  fix2_dy = 0.015
c1     = log(fix1_x + gamma)
m      = fix2_dy * (fix2_x + gamma)
q      = fix1_y - m * c1

speed_mapped = log(gamma + filtered_speed_px_per_sec) * m + q
```

### 3.3 Radius Clamps, `opaque_linearize`, Offsets, and Snapping

- **Radius bounds:** brush core clamps dynamic radius to `[ACTUAL_RADIUS_MIN, ACTUAL_RADIUS_MAX] = [0.2, 1000.0]` px (`R_base = clamp(exp(base(radius_logarithmic)), 0.2, 1000.0)`). Surface skips dabs when `radius < 0.1`, `hardness == 0`, or `opaque == 0`.
- **Opacity linearization (`opaque_linearize` base value != 0):**
  ```text
  opaque         = clamp(max(0.0, SETTING(opaque)) * SETTING(opaque_multiply), 0.0, 1.0)
  dabs_per_pixel = max(1.0, (dabs_per_actual_radius + dabs_per_basic_radius) * 2.0)
  dabs_per_pixel = 1.0 + base(opaque_linearize) * (dabs_per_pixel - 1.0)
  opaque         = 1.0 - pow(1.0 - opaque, 1.0 / dabs_per_pixel)
  ```
- **Position offsets & `FLIP`:** `FLIP` alternates `+1` / `-1` on every emitted dab. Apply in order:
  1. `directional_offsets()` (`offset_angle*`, `offset_x`, `offset_y`) scaled by `exp(offset_multiplier) * base_radius` with `FLIP` on paired arms.
  2. Speed offset: `(norm_dx_slow, norm_dy_slow) * (offset_by_speed * 0.1 / viewzoom)`.
  3. Random jitter: 2D Irwin–Hall Gaussian (§4.3) scaled by `offset_by_random * base_radius`.
  4. `radius_by_random`: Irwin–Hall Gaussian in log-radius space, re-clamped, with conditional opacity compensation when noisy radius expands.
- **Geometric anti-aliasing & `snap_to_pixel`:** if fadeout width `radius * (1 - hardness) < anti_aliasing`, reparameterize `(radius, hardness)` before submission to preserve optical area while widening the ramp. When `snap_to_pixel > 0`, lerp center toward `floor(p) + 0.5` and radius toward `0.5` px multiples (subtracting a small epsilon near `1.0` to avoid neighbor bleed).

### 3.4 Smudge Buckets, Pickup Gate, and HSV/HSL Color Dynamics

- **Bucket layout (`mypaint_brush_new_with_buckets(n)`, max `256`):** 9 floats per bucket — `SMUDGE_R/G/B/A`, `PREV_COL_R/G/B/A`, `PREV_COL_RECENTNESS`; selected via `clamp(round(smudge_bucket), 0, n - 1)`.
- **Pickup cadence & early abort:**
  ```text
  update_factor = max(0.01, smudge_length)
  recentness    = PREV_COL_RECENTNESS * update_factor
  resample      = recentness < min(1.0, pow(0.5 * update_factor, smudge_length_log) + margin)
  ```
  On resample, reset `recentness = 1.0` and call `mypaint_surface_get_color` with `smudge_radius = clamp(radius * exp(smudge_radius_log), 0.2, 1000.0)` (passing `paint = -1.0` when the `legacy_smudge` compatibility branch applies). If `smudge_transparency` triggers (sampled alpha below positive threshold, or inverted for negative), **abort the dab before drawing**.
- **Smudge apply → eraser → HSV → HSL (strict sequence):**
  1. `update_smudge_color`: EMA RGBA blend (or spectral WGM with low-alpha damping when pigment active).
  2. `apply_smudge`: `smudge_factor = min(1.0, smudge)`; `eraser_target_alpha = clamp((1.0 - smudge_factor) + smudge_factor * smudge_alpha, 0.0, 1.0)`; mix bucket color into brush RGB (initialized from `base_value(color_h/s/v)`).
  3. `eraser_target_alpha *= (1.0 - eraser)`.
  4. If `linear == TRUE` and any color dynamic is non-zero, convert RGB with `pow(c, 1.0 / 2.2)` before steps 5–6 and `pow(c, 2.2)` after.
  5. **HSV dynamics:** `h = fract(h + change_color_h)`; `s += s * v * change_color_hsv_s`; `v += change_color_v` → RGB.
  6. **HSL dynamics (after HSV):** `l += change_color_l`; `s += s * min(abs(1.0 - l), abs(l)) * 2.0 * change_color_hsl_s` → RGB.

---

## 4. Surface Sampling, Spectral Constants, and Deterministic RNG

Tile layout (`64x64` premultiplied `uint16` with `1 << 15 = 32768` full scale, `(xp + 0.5, yp + 0.5)` centers, `r + 1` tile fringe, `tile_request_start`/`end`, and blend-pass ordering) lives in [surface-layer-gpu.md](surface-layer-gpu.md) §§2–6.

### 4.1 `get_color` Adaptive Subsampling (`mypaint-tiled-surface.c`)

Before reading any overlapped tile in `get_color`, flush its pending queue via `process_tile_internal()`. Pickup always uses circular soft mask parameters (`hardness = 0.5`, `aspect_ratio = 1.0`, `angle = 0.0`, `radius = max(smudge_radius, 1.0)`):

```text
if radius <= 2.0:
    sample_interval = 1;                  random_sample_rate = 1.0
else:
    sample_interval = int(radius * 7.0);  random_sample_rate = 1.0 / (7.0 * radius)
```

Accumulate `sum_weight += mask_opa / 32768` and `sum_a += mask_opa * px_a / 32768^2`. Additive path accumulates `sum_rgb += mask_opa * px_rgb / 32768`, normalizes by `sum_weight`, and de-premultiplies by `result_a`. Spectral path blends `avg_spectral[i] = spectral_px[i]^fac_a * avg_spectral[i]^fac_b` (`fac_a = new_a / (old_sum_a + new_a)`) and lerps `spectral_to_rgb(avg_spectral)` with additive RGB by `paint` to suppress dark low-alpha fringes.

### 4.2 10-Band Spectral Upsampling & T-Matrix (`helpers.c`)

```c
// WGM_EPSILON = 0.0001f (prevents log(0)/0^fac collapse; tied to T_MATRIX_SMALL)
static const float spectral_r[10] = {
    0.00928f, 0.00973f, 0.01125f, 0.01511f, 0.02480f,
    0.08362f, 0.97787f, 1.00000f, 0.99996f, 1.00000f};
static const float spectral_g[10] = {
    0.00285f, 0.00392f, 0.01213f, 0.74826f, 1.00000f,
    0.86570f, 0.03748f, 0.02282f, 0.02175f, 0.02138f};
static const float spectral_b[10] = {
    0.53705f, 0.54665f, 0.57550f, 0.25878f, 0.04171f,
    0.01266f, 0.00749f, 0.00677f, 0.00670f, 0.00668f};

static const float T_MATRIX_SMALL[3][10] = {
    { 0.02660f,  0.04978f,  0.02245f, -0.21845f, -0.25689f,
      0.44588f,  0.77237f,  0.19450f,  0.01404f,  0.00769f},
    {-0.03260f, -0.06102f, -0.05249f,  0.20666f,  0.57250f,
      0.31784f, -0.02122f, -0.01939f, -0.00152f, -0.00084f},
    { 0.33948f,  0.63540f,  0.77152f,  0.11322f, -0.05525f,
     -0.04822f, -0.01297f, -0.00152f, -0.00009f, -0.00005f}};
```

- **RGB → Spectral:** `c_adj = c * (1.0f - 0.0001f) + 0.0001f`; `spec[i] = spectral_r[i]*r_adj + spectral_g[i]*g_adj + spectral_b[i]*b_adj`.
- **WGM mix:** `fac_a = opa_a / (opa_a + opa_b * (dst_a / 32768.0f))`, `fac_b = 1.0f - fac_a`; `out_spec[i] = powf(spec_a[i], fac_a) * powf(spec_b[i], fac_b)`.
- **Spectral → RGB:** `rgb[c] = clamp((dot(T_MATRIX_SMALL[c], spec) - 0.0001f) / (1.0f - 0.0001f), 0.0f, 1.0f)`.

### 4.3 Knuth LFIB RNG & Irwin–Hall Gaussian (`rng-double.*`)

- **PRNG:** Knuth lagged Fibonacci generator initialized by `rng_double_new(seed)` with `KK = 10`, `LL = 7`, `QUALITY = 19`, producing `double` in `[0, 1)`.
- **4-sample Irwin–Hall Gaussian (`~N(0, 1)`):**
  ```text
  rand_gauss = (rng_next() + rng_next() + rng_next() + rng_next()) * 1.73205080757 - 3.46410161514
  ```
  Used by `tracking_noise`, `offset_by_random`, and `radius_by_random`. Consuming fewer/more RNG draws per dab breaks cross-backend determinism.

---

## 5. Reference GPU Surface Kernels (SkSL & Vulkan GLSL)

Architecture, staging, barriers (`SHADER_WRITE → SHADER_READ` before `get_color` reduction readback), and rollout order live in [surface-layer-gpu.md](surface-layer-gpu.md) §§9–10.

### 5.1 Skia `SkRuntimeEffect` Dab Coverage (SkSL)

Normal/Eraser maps to `SkBlendMode::kSrcOver` and Lock-Alpha to `SkBlendMode::kSrcATop` per `64x64` `SkSurface` flushed at `end_atomic`; Colorize, Posterize, and Spectral require `SkRuntimeEffect` shaders:

```glsl
uniform float2 center;
uniform float radius, aspect_ratio, angle, hardness;

float dab_opa(float2 pos) {
    float2 d = pos - center;
    float cs = cos(angle), sn = sin(angle);
    float xxr = d.y * sn + d.x * cs;
    float yyr = (d.y * cs - d.x * sn) * aspect_ratio;
    float rr  = (xxr * xxr + yyr * yyr) / (radius * radius);
    if (rr > 1.0) return 0.0;
    return (rr <= hardness)
        ? 1.0 - rr * (1.0 / hardness - 1.0)
        : (hardness / (1.0 - hardness)) * (1.0 - rr);
}
```

### 5.2 Vulkan Compute Tile Kernel & Premultiplied Blend Passes (GLSL)

Bind each `64x64` tile as `rgba16` (`VK_IMAGE_LAYOUT_GENERAL`, `R16G16B16A16_UNORM` scaled by `32768/65535` or `R16G16B16A16_SFLOAT`), dispatch `(8, 8, 1)` workgroups of `local_size_x = 8, local_size_y = 8` (`gl_GlobalInvocationID.xy` spans `0..63`), and replay queued `DabParams` strictly in submission order per pixel. Below, `dab_opa(vec2, DabParams)` evaluates the rotated/elliptical piecewise-linear falloff from §5.1 against `DabParams` geometry, `set_lum(vec3, float)` applies Cairo/PDF luminance substitution with channel clipping, and `apply_blend_passes` executes the ordered composite sequence specified in [surface-layer-gpu.md](surface-layer-gpu.md) §5 (`Normal`/`LockAlpha` additive when `paint < 1`, `Normal_Paint`/`LockAlpha_Paint` spectral WGM when `paint > 0`, `Colorize`, `Posterize`):

```glsl
layout(local_size_x = 8, local_size_y = 8) in;

struct DabParams {
    vec2 center;
    float radius, aspect_ratio, angle, hardness;
    float r, g, b, opaque;
    float target_a, lock_alpha, colorize, posterize, posterize_num, paint;
};

layout(set = 0, binding = 0, rgba16) uniform image2D tile;
layout(set = 0, binding = 1) readonly buffer DabList { DabParams dabs[]; };
layout(push_constant) uniform PC { int num_dabs; ivec2 tile_origin; };

// Schematic helpers (see §5.1 for mask falloff and surface-layer-gpu.md §5 for pass order):
float dab_opa(vec2 pos, DabParams d);
vec3 set_lum(vec3 c, float lum);
vec4 apply_blend_passes(vec4 dst, DabParams d, float mask_opa);

vec4 blend_normal(vec4 dst, vec3 src_rgb, float src_a, float opa_w) {
    float inv = 1.0 - opa_w;
    return vec4(opa_w * src_a * src_rgb + inv * dst.rgb, opa_w * src_a + inv * dst.a);
}

vec4 blend_lock_alpha(vec4 dst, vec3 src_rgb, float opa_w) {
    return vec4((opa_w * dst.a) * src_rgb + (1.0 - opa_w) * dst.rgb, dst.a);
}

// Rec.709 luma: dot(c, vec3(0.2126, 0.7152, 0.0722))
vec4 blend_colorize(vec4 dst, vec3 src_rgb, float opa_w) {
    vec3 dst_s = dst.a > 0.0 ? dst.rgb / dst.a : vec3(0.0);
    vec3 recolored = set_lum(src_rgb, dot(dst_s, vec3(0.2126, 0.7152, 0.0722)));
    return vec4(opa_w * recolored * dst.a + (1.0 - opa_w) * dst.rgb, dst.a);
}

void main() {
    ivec2 local_px = ivec2(gl_GlobalInvocationID.xy);
    vec2 px_center = vec2(tile_origin + local_px) + vec2(0.5);
    vec4 color = imageLoad(tile, local_px);
    for (int i = 0; i < num_dabs; i++) {
        float opa = dab_opa(px_center, dabs[i]);
        color = apply_blend_passes(color, dabs[i], opa);
    }
    imageStore(tile, local_px, color);
}
```

