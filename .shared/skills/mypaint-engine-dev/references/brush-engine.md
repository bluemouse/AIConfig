# libmypaint Brush Engine

Load this reference for `.myb` presets, setting mappings, input processing, stroke-to-dab planning, deterministic replay, color dynamics, smudge, pigment, or implementing a compatible brush core.

## 1. Engine boundary

libmypaint is a dab engine, not a polyline renderer. The brush core receives timestamped input samples, updates internal state, emits zero or more dabs, and calls surface callbacks. It should not know whether the surface is CPU tiles, Skia, Vulkan, or another backend.

```text
input sample stream
  -> sanitize and derive inputs
  -> virtual cursor and filtered state
  -> mapping evaluation
  -> dab scheduler
  -> per-dab color/geometry assembly
  -> surface draw_dab / get_color
```

Use `mypaint_brush_stroke_to()` with explicit `viewzoom`, `viewrotation`, and `barrel_rotation`. Pass `linear=TRUE` when color dynamics must run in linear sRGB. Submit dabs through `mypaint_surface_draw_dab()`, which carries `paint` (spectral pigment), `posterize`, `lock_alpha`, and `colorize`.

## 2. Preset data model

A `.myb` preset consumed by libmypaint has this shape:

```json
{
  "version": 3,
  "settings": {
    "radius_logarithmic": {
      "base_value": 1.0,
      "inputs": {
        "pressure": [[0.0, -1.5], [1.0, 1.5]]
      }
    }
  }
}
```

Rules:

- `version` must be 3.
- `settings` must exist.
- Unknown settings/inputs should warn and skip the invalid entry.
- Metadata such as brush name, group, comments, or restore-color behavior may be host-side and should not be treated as brush simulation state unless libmypaint consumes it.

Setting value formula:

```text
setting_value = base_value + sum(curve_i(input_i))
```

Important setting families:

- Geometry and coverage: `radius_logarithmic`, `hardness`, `anti_aliasing`, `opaque`, `opaque_multiply`, `opaque_linearize`, `elliptical_dab_ratio`, `elliptical_dab_angle`, `snap_to_pixel`.
- Spacing and timing: `dabs_per_actual_radius`, `dabs_per_basic_radius`, `dabs_per_second`.
- Stabilization and derived inputs: `slow_tracking`, `slow_tracking_per_dab`, `tracking_noise`, `speed1_slowness`, `speed2_slowness`, `direction_filter`, `custom_input`, `custom_input_slowness`.
- Offsets and randomization: `offset_by_random`, `offset_by_speed`, `radius_by_random`, `offset_x`, `offset_y`, `offset_angle*`, `offset_multiplier`.
- Color and paint: `color_h`, `color_s`, `color_v`, `change_color_h`, `change_color_v`, `change_color_l`, `change_color_hsv_s`, `change_color_hsl_s`, `eraser`, `lock_alpha`, `colorize`, `posterize`, `posterize_num`, `paint_mode`.
- Smudge: `smudge`, `smudge_length`, `smudge_length_log`, `smudge_radius_log`, `smudge_bucket`, `smudge_transparency`.

## 3. Mapping curves

Each setting/input mapping has 0 or 2..64 points. Exactly 1 point is invalid. X values must be non-decreasing.

Evaluation is piecewise linear and extrapolates beyond endpoints using the first or last segment slope. Do not clamp outside the curve domain unless intentionally designing a non-compatible engine.

Pseudo-code:

```text
value = base_value
for each input mapping:
  choose the segment containing input x
  if x is before first point: use first segment
  if x is after last point: use last segment
  if segment has equal x or equal y: y = y0
  else y = linear_interpolate(x0,y0,x1,y1,x)
  value += y
```

Speed inputs are filtered and remapped logarithmically. The speed remap coefficients are precomputed from base values of `speed1_gamma` and `speed2_gamma`. Do not recompute them from dynamic mapped values.

## 4. Input processing

A single input sample includes canvas coordinates, pressure, xtilt, ytilt, dt, view zoom, view rotation, and optionally barrel rotation. Process it as follows:

1. Clamp or sanitize raw values.
   - `pressure <= 0` becomes 0.
   - `dt <= 0` becomes a small positive epsilon.
   - very large `dt` or invalid positions trigger a reset/split boundary.
   - `xtilt` and `ytilt` are clamped to [-1, 1].
2. Convert tilt:
   - `tilt_ascension = degrees(atan2(-xtilt, ytilt))`
   - `tilt_declination = 90 - hypot(xtilt, ytilt) * 60`
   - `tilt_declinationx = xtilt * 60`
   - `tilt_declinationy = ytilt * 60`
3. Apply virtual cursor behavior: tracking noise and slow tracking.
4. Compute derived inputs used by mappings: pressure, speed1, speed2, random, stroke, direction, direction_angle, tilt channels, attack_angle, barrel_rotation, viewzoom, brush_radius, gridmap_x/y, and custom.

Ordering matters: settings should observe the current filtered state before the current step is integrated for the next sample.

## 5. Dab scheduling

Dab count for a remaining segment is additive:

```text
count = distance/current_radius * dabs_per_actual_radius
      + distance/base_radius    * dabs_per_basic_radius
      + dt                      * dabs_per_second
```

For elliptical dabs, measure distance in the rotated/aspect-scaled dab coordinate frame.

Use the recompute loop:

```text
dabs_moved = partial_dabs
dabs_todo = count_dabs_to(target, dt)
dt_left = dt

while dabs_moved + dabs_todo >= 1:
  step_ddab = (1 - dabs_moved) if dabs_moved > 0 else 1
  dabs_moved = 0
  frac = step_ddab / dabs_todo
  step_dt = frac * dt_left
  interpolate x/y/pressure/tilt/barrel rotation by frac
  update state and evaluate settings for this step
  flip *= -1
  draw_dab()
  random_input = rng_next()
  dt_left -= step_dt
  dabs_todo = count_dabs_to(target, dt_left)

update state without drawing for the remaining fractional step
partial_dabs = dabs_moved + dabs_todo
```

Do not simplify this to `partial += count; draw floor(partial)`. Dynamic radius, spacing, and ellipse state can change inside a single input event.

## 6. Per-dab assembly

Resolve each dab in this order:

1. Compute opacity from `opaque * opaque_multiply`, then apply `opaque_linearize` if needed.
2. Start at tracked position.
3. Apply directional offsets, speed offset, and random offset.
4. Resolve radius, including `radius_by_random`, and clamp to legal range.
5. Build color from HSV base values.
6. Perform smudge pickup/update/apply if active.
7. Apply eraser target alpha.
8. Apply HSV dynamics, then HSL dynamics.
9. Apply geometry refinements: hardness, anti-aliasing minimum, snap-to-pixel.
10. Submit to `mypaint_surface_draw_dab()` with lock-alpha, colorize, posterize, and paint-mode fields.

`FLIP` alternates each emitted dab and affects paired directional-offset arms. This is also why multi-bucket smudge exists.

## 7. Smudge and pigment

Smudge is stateful. A bucket stores smudge RGBA, previous sampled color RGBA, and recentness. Multi-bucket brushes select a bucket with `smudge_bucket` so multiple dab arms do not share wet-state incorrectly.

Smudge order:

```text
base HSV -> RGB
pickup canvas color if recentness threshold requires it
update smudge bucket
mix bucket into brush color
adjust eraser target alpha from smudge alpha
apply eraser
apply HSV dynamics
apply HSL dynamics
```

`get_color` must flush queued operations before sampling the tile buffer or smudge will read stale pixels.

`paint_mode` blends additive RGB and spectral pigment behavior. Spectral mixing uses a 10-band representation and weighted geometric mean. Add spectral/GPU parity last in a new implementation because it is the hardest to validate and the easiest to make non-deterministic.

## 8. Determinism contract

For a compatible engine, identical preset, seed, initial state, input samples, surface contents, and color-space mode should produce identical dab parameters and matching output.

Determinism hazards:

- RNG advanced per input event instead of per emitted dab.
- Mapping curves clamped instead of extrapolated.
- Missing post-loop state update when no dab is emitted.
- Reordered smudge/color dynamics.
- Parallel surface blending that changes per-tile operation order.
- GPU readback of `get_color` before pending draws are flushed.
