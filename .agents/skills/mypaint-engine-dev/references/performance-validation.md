# Performance, Resource Management, Debugging, and Validation

Load this reference for live drawing performance, memory/resource management, profiling, debugging, regression testing, golden images, or architecture tradeoffs.

## 1. Live drawing performance model

Live drawing latency is the sum of:

```text
input sampling -> app dispatch -> brush core sequential update -> surface queueing -> tile processing -> dirty-region propagation -> layer/display composite
```

The brush core is mostly sequential. The surface backend and display compositor are where most safe parallelism lives.

## 2. Hot-path rules

- Avoid per-dab heap allocation in new code. Pool dab operations, tile work items, masks, command buffers, and temporary color buffers.
- Preserve operation order within a tile. Parallelize across tiles or across pixels within one ordered dab list.
- Keep preset parsing and resource resolution out of the per-event path.
- Keep UI state reads out of native brush rendering. Copy host color/settings into brush values before the stroke.
- Avoid GPU readbacks except when `get_color`/smudge requires them; batch and throttle when possible.
- Keep dirty bboxes tight but complete. Too small causes stale display; too large burns compositor time.
- Treat very large radii, offsets, and pathological mapping curves as resource-exhaustion risks; clamp or guard where libmypaint does.

## 3. Resource management

Preset/resource boundaries:

- `.myb` preset data: user-facing brush settings and mappings.
- `BrushInfo`: editable host representation.
- `Brush`: live engine state and native mapping mirror.
- Surface/layer resources: tiles, cached display surfaces, dirty regions, and optional GPU textures.

For a new painting app, store enough metadata to replay strokes deterministically:

- original preset payload or canonicalized settings;
- brush engine version;
- input sample stream with timestamps/dt;
- initial brush state or reset policy;
- random seed;
- color-space path;
- surface initial pixels and symmetry state.

## 4. Debugging workflow

1. Reproduce with a minimal preset and a short input stream.
2. Decide whether the failure is dab sequence or pixel compositing.
3. Log per-dab parameters before surface submission:
   - x/y, radius, hardness, opacity;
   - aspect ratio and angle;
   - color and eraser target alpha;
   - lock-alpha/colorize/posterize/paint-mode;
   - RNG index or random input;
   - smudge bucket and sampled color.
4. If dab parameters match but output differs, debug surface mask, blend order, pixel format, premultiplication, and dirty regions.
5. If dab parameters differ, debug input sanitization, mapping evaluation, speed remap, scheduler recompute loop, and RNG advancement.

Use `<SKILL_ROOT>/scripts/mypaint_source_probe.py` with local checkouts to verify key source files and symbol anchors before citing or modifying code paths.

## 5. Unit tests

Test these before visual output:

- `.myb` parser: version, missing settings, unknown settings/inputs, invalid mapping point counts.
- Mapping interpolation and extrapolation.
- Input sanitization and tilt derivation.
- Speed logarithmic remap coefficient calculation.
- Dab count formula and partial dab carry.
- Scheduler recomputation after each dab.
- Shortest-angle interpolation for ascension/barrel rotation.
- RNG advancement exactly once per emitted dab.
- Smudge bucket selection and recentness decay.
- Pixel `rr` calculation and falloff at center, `rr=hardness`, edge, and outside.
- Premultiplied blend formulas and 32768 scale.

## 6. Determinism tests

For the same seed, preset, initial state, and input stream:

- Run the brush core twice and compare emitted `DabOp` sequences byte-for-byte where feasible.
- Change event packetization while preserving the same geometric path and verify expected, documented differences.
- Replay across CPU/GPU backends and compare final images within an explicit tolerance.
- Confirm no worker/thread scheduling nondeterminism changes same-tile operation ordering.

## 7. Visual parity tests

Generate golden images with libmypaint or the trusted CPU reference:

- pressure taper brush;
- speed-sensitive opacity/radius brush;
- tilt/rotation elliptical brush;
- slow tracking/stabilizer brush;
- scatter/random offset and radius noise brush;
- eraser and lock-alpha over semi-transparent pixels;
- colorize over varied luminance;
- smudge over colored checkerboard;
- multi-bucket smudge with offset arms;
- posterize brush;
- pigment `paint_mode` brush;
- symmetry: vertical, horizontal, rotational, snowflake;
- small hard dabs for anti-aliasing.

Use both pixel-difference metrics and human visual review. Small mathematical errors in falloff or premultiplication can be very visible in strokes.

## 8. Performance benchmarks

Benchmark these separately:

- brush-core event throughput without surface writes;
- dabs emitted per second for common presets;
- CPU tile blend throughput by radius and opacity;
- dirty-region display recomposition cost;
- smudge `get_color` cost by radius;
- GPU upload/dispatch/readback cost per atomic update;
- memory growth and tile allocation churn for large canvases;
- long-stroke latency distribution, not only average FPS.

Record p50/p95/p99 latency. Artists feel tail latency during live drawing.

## 9. Optimization checklist

- Cache mapping constant paths and speed remap coefficients.
- Pool or stack-allocate small per-tile masks when CPU rendering.
- Reuse operation queues and avoid per-tile hash churn in tight loops.
- Batch dirty rectangles but do not over-invalidate whole canvas regions.
- Use tile-level task parallelism for CPU compositing.
- Use GPU compute for pixel loops; keep brush state on CPU unless redesigning with exact parity tests.
- Avoid de-premultiply/re-premultiply cycles unless required by colorize, pickup, or display conversion.
- Add hard limits or graceful fallbacks for extreme radius and offset settings.
