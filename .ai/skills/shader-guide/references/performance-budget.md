# performance-budget: Real-Time Effect Limits

## Guideline

Keep per-pixel work within fixed iteration budgets so effects remain interactive on modest GPUs and software rasterizers — cap ray-march steps, volume samples, FBM octaves, and total nested loop work.

## Rationale

Creative shaders often nest loops (march × shadow × AO × FBM). Each layer multiplies cost; exceeding ~1000 effective inner iterations per pixel commonly stalls the GPU and freezes interactive hosts.

## Default Budgets

| Category | Limit | Notes |
|---|---|---|
| Ray marching main loop | ≤ 128 steps | Raise only after SDF is tight and early-out is working |
| Volume / lighting inner loops | ≤ 32 steps | Clouds, fog, soft-shadow refinement |
| FBM octaves | ≤ 6 layers | Ridged or domain-warped FBM stacks cost more — reduce octaves first |
| Total nested iterations / pixel | ≤ 1000 | Product of nested loops; exceeding this risks frame stalls |

## How to Apply

1. Start with half the budget (64 march steps, 4 FBM octaves) until the image is correct.
2. Visualize step count heatmaps per [shader-debugging](shader-debugging.md) before increasing `MAX_STEPS`.
3. Prefer analytic shortcuts ([analytic-ray-tracing](analytic-ray-tracing.md), cheaper AO) over deeper loops.
4. Use bounding volumes and [sdf-tricks](sdf-tricks.md) to skip empty space in march loops.
5. For multi-pass sims, move heavy solvers to [multipass-buffer](multipass-buffer.md) passes with lower resolution.

## Example

```glsl
#define MAX_STEPS 128
#define MAX_DIST 100.0
#define FBM_OCTAVES 6

for (int i = 0; i < MAX_STEPS; i++) {
    float d = map(p);
    if (d < SURF_DIST) break;
    t += d;
    if (t > MAX_DIST) break;
}
```

## Gotchas

- Increasing march steps on a divergent SDF wastes fill rate — fix distance field correctness first.
- Shadow loops stacked on AO loops stacked on FBM in the same pixel multiply cost — stage them or lower inner limits.
- `#define MAX_STEPS 256` without early exit does not help if most rays miss late — use tighter scene bounds.

## Combine With

- [shader-debugging](shader-debugging.md)
- [ray-marching](ray-marching.md)
