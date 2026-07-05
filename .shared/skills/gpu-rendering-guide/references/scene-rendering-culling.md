# scene-rendering-culling: Scene Visibility and Draw Submission

## Guideline

Determine visible geometry before recording draws; emit draw commands sorted by pipeline state and material to minimize state changes; use instancing or auto-instancing for repeated geometry; and treat anything that changes the bound pipeline, shader variant, or binding group as a batch breaker.

## Rationale

Recording one draw per object in scene order maximizes pipeline and binding churn — the GPU spends more time switching state than shading. Production engines (Unreal mesh pass processors, Frostbite sort-key scheduling, Unity's batching passes) instead build a flat list of visible draws, sort it by a 64-bit key encoding pipeline/material/mesh, and record in that order so consecutive draws share state. Culling runs first so invisible geometry never enters the list: frustum culling on the CPU for coarse rejection, hierarchical Z or occlusion queries for fine rejection, and optionally GPU-side culling when draw counts exceed what the CPU can enumerate.

## How to Apply

1. **Cull first** — Build a visible set per view: frustum test bounding volumes, then optional occlusion (Hi-Z, software raster, or GPU cull pass).
2. **Flatten to draw commands** — Each visible mesh/submesh becomes a draw record carrying mesh handle, material handle, transform index, and sort key.
3. **Sort by state** — Encode sort key as: pipeline/PSO (high bits) → material/shader variant → mesh → depth (for opaque front-to-back or transparent back-to-front).
4. **Record in sorted order** — Walk the sorted list; rebind only when the sort key's state group changes.
5. **Instancing** — Merge draws that share identical state and mesh but differ only in transform into one instanced draw with a per-instance buffer.
6. **Parallel record** — Workers can each record a chunk of the sorted list into secondary streams; merge with sort keys if workers don't preserve global order, see [references/command-recording-and-frames.md](./command-recording-and-frames.md).

## Example

```c
// Build visible draws, sort by PSO then material, record with minimal rebinding.
typedef struct {
    uint64_t sort_key;   // [pso_id:16][mat_id:16][mesh_id:16][depth:16] — IDs, not handles
    uint32_t index_count, first_index;
    uint32_t transform_index;
} draw_cmd;

void submit_visible_pass(view *v, cmd_stream cmd,
                         pipeline *pso_table, material *mat_table) {
    int n = 0;
    draw_cmd *draws = cull_and_build_draws(v, &n);    // frustum + optional occlusion
    qsort(draws, n, sizeof(draw_cmd), cmp_sort_key);    // state-major order

    pipeline current_pso = PIPELINE_NONE;
    material current_mat = MATERIAL_NONE;
    for (int i = 0; i < n; ++i) {
        uint16_t pso_id = (uint16_t)(draws[i].sort_key >> 48);
        uint16_t mat_id = (uint16_t)((draws[i].sort_key >> 32) & 0xFFFF);
        pipeline pso = pso_table[pso_id];
        material mat = mat_table[mat_id];
        if (pso != current_pso) { cmd_bind_pipeline(cmd, pso); current_pso = pso; }
        if (mat != current_mat) { cmd_bind_group(cmd, 1, mat.group); current_mat = mat; }
        cmd_push_constants(cmd, STAGE_VERTEX, &draws[i].transform_index, 4);
        cmd_draw_indexed(cmd, draws[i].index_count, draws[i].first_index);
    }
}
```

## Gotchas

- Sorting opaque front-to-back and transparent back-to-front are different policies — use separate passes or encode pass type in the sort key; don't mix them in one sorted stream.
- A "visible" draw that changes shader variant per object defeats batching — variant selection must happen at material granularity, not per object, see [references/shader-system.md](./shader-system.md).
- CPU culling that touches every object every frame becomes the bottleneck at scale; move cull+compact to the GPU when draw counts exceed ~10k, see [references/gpu-driven-rendering.md](./gpu-driven-rendering.md).
- Instancing requires identical mesh topology and shader path; different LOD levels or skinning variants are separate batches even if the mesh looks similar.
- Occlusion culling with stale depth or wrong projection culls visible geometry silently — validate with a debug overlay that draws culled bounds.

## Related

[references/command-recording-and-frames.md](./command-recording-and-frames.md), [references/binding-model.md](./binding-model.md), [references/gpu-driven-rendering.md](./gpu-driven-rendering.md)
