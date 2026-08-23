# Surface, Layers, Pixels, Symmetry, and GPU Backends

Load this reference for pixel math, tiled surfaces, compositing, layer integration, dirty regions, symmetry, graphics API integration, Skia, Vulkan, or rendering backend design.

## 1. Layer and surface boundary

MyPaint layers own document semantics. libmypaint surfaces own pixel execution. A painting layer wraps each incremental brush update in an atomic surface block:

```text
layer.begin_atomic()
  brush.stroke_to(surface, x, y, pressure, tilt, dt, view...)
layer.end_atomic() -> dirty bbox
```

The surface can defer dab operations until `end_atomic`, but it must preserve operation order within each affected tile. Dirty regions must include every written pixel, including symmetry copies and edge fringe.

## 2. Tile storage

libmypaint uses sparse 64x64 tiles.

```text
tile_x = floor(pixel_x / 64)
tile_y = floor(pixel_y / 64)
```

Each tile stores premultiplied RGBA as 16-bit integers, but the logical full scale is 32768 (`1 << 15`), not 65535:

```text
R, G, B are premultiplied by A
A = 32768 means fully opaque
float = channel16 / 32768.0
```

Using 15-bit scale keeps channel products within 32-bit integer arithmetic.

Pixel centers are `(x + 0.5, y + 0.5)`. Using integer pixel corners shifts small or hard dabs.

## 3. Dab footprint and operation queue

A dab with center `(x, y)` and radius `r` touches tiles overlapped by `r + 1` fringe:

```text
tx1 = floor(floor(x - (r + 1)) / 64)
tx2 = floor(floor(x + (r + 1)) / 64)
ty1 = floor(floor(y - (r + 1)) / 64)
ty2 = floor(floor(y + (r + 1)) / 64)
```

CPU tiled surface design:

1. `draw_dab` validates parameters and creates an operation.
2. The operation is copied into every affected tile's queue.
3. The dirty bbox expands.
4. `end_atomic` processes queued operations per tile, in order, possibly in parallel across independent tiles.

Do not parallelize by reordering operations within the same tile.

## 4. Dab rasterization

Per pixel, compute normalized squared elliptical distance:

```text
dx = (pixel_x + 0.5) - dab_x
dy = (pixel_y + 0.5) - dab_y
cs = cos(angle)
sn = sin(angle)
xxr = dy * sn + dx * cs
yyr = (dy * cs - dx * sn) * aspect_ratio
rr = (xxr*xxr + yyr*yyr) / (radius*radius)
```

Opacity falloff is piecewise linear in `rr`, not Gaussian:

```text
if rr > 1: opa = 0
else if rr <= hardness:
  opa = 1 + rr * -(1/hardness - 1)
else:
  opa = hardness/(1-hardness) + rr * -hardness/(1-hardness)
```

Guard rails:

- radius below the surface threshold: skip.
- hardness == 0: skip.
- opaque == 0: skip.

For very small dabs, the CPU path uses an analytical anti-aliasing path. GPU backends may use multisampling or analytic coverage, but must be validated against reference images for small hard brushes.

## 5. Composite passes

Blend pass order is parity-critical:

1. Normal additive/RGB path.
2. Normal pigment path when `paint_mode > 0`.
3. Lock-alpha additive path.
4. Lock-alpha pigment path when `paint_mode > 0`.
5. Colorize.
6. Posterize.

The normal contribution is reduced by mode exclusivity:

```text
normal = (1 - lock_alpha) * (1 - colorize) * (1 - posterize)
```

All compositing assumes premultiplied destination pixels. `eraser` is represented through target alpha/color alpha, not by switching to a separate eraser renderer.

## 6. Canvas color pickup

Smudge uses `get_color` to average canvas color under a circular soft region. Requirements:

- Use hardness 0.5, aspect ratio 1, angle 0 for pickup mask.
- Enforce minimum radius of 1 pixel.
- Flush pending operations affecting sampled tiles before reading pixels.
- Return de-premultiplied color to the brush core where expected.
- For pigment paths, preserve the spectral/additive split and alpha weighting.

GPU readback is expensive. Respect smudge pickup throttling; do not sample every dab unless the brush settings require it.

## 7. Symmetry and mirroring

Viewport mirroring is display-only. Painting symmetry belongs to surface/model space and duplicates dabs.

Tiled-surface symmetry flow (`MyPaintTiledSurface`):

```text
pending symmetry state set from layer tree
begin_atomic refreshes transform matrices
draw original dab
for each active symmetry transform:
  transform dab center and angle
  draw duplicate dab through same internal draw path
```

Supported families include vertical, horizontal, vertical plus horizontal, rotational N-fold, and snowflake-style reflected rotational copies. Dirty regions must include all copies.

## 8. Display and UI workflow

A painting app built around this model should have two rendering paths:

- Stroke path: brush dabs write into layer surfaces.
- Display path: layer stack composites surfaces into the viewport with zoom, pan, rotation, and view mirroring.

Do not let viewport transforms mutate layer pixel coordinates. Convert input device coordinates into document coordinates before calling the brush core. Convert dirty bboxes back into viewport update regions for repaint.

## 9. GPU backend strategy

Recommended split:

```text
CPU brush core: input -> mapping -> dab list -> per-tile operation queues
GPU surface: tile textures -> compute/fragment rasterization -> blend passes -> display composite
```

The brush core is sequential because each emitted dab depends on previous state. Pixel blending is parallel and belongs on the GPU.

### Vulkan design

- Store each tile as a region or layer in `R16G16B16A16_UNORM` or `R16G16B16A16_SFLOAT` texture storage.
- Upload per-tile `DabOp` buffers at `end_atomic`.
- Dispatch compute workgroups over affected tiles or affected pixel ranges.
- Run dabs in exact queued order for each pixel.
- Insert barriers before display sampling or `get_color` readback.
- Pool command buffers, staging buffers, descriptor sets, and tile allocations.

### Skia/Skiko design

- Use a shader/effect for the dab mask falloff.
- Use normal blend modes where they match, and custom runtime effects for colorize, posterize, pigment, and exact lock-alpha semantics.
- Batch per atomic update and flush at `end_atomic`.
- Keep CPU reference parity tests because Skia blend modes will not exactly cover every libmypaint mode.

## 10. GPU implementation order

1. Build a CPU reference surface with exact libmypaint math.
2. Validate mapping, dab sequence, and pixels against libmypaint.
3. Add GPU Normal-mode only.
4. Add lock-alpha, eraser, colorize, and posterize.
5. Add smudge with explicit flush/readback handling.
6. Add pigment/spectral blending last.
7. Optimize only after visual parity gates pass.
