# gpu-driven-rendering: GPU Culling and Indirect Draw

## Guideline

When draw counts exceed what the CPU can cull and submit each frame, move visibility determination and draw compaction to the GPU; emit draw/dispatch counts via indirect arguments sourced from GPU buffers so the CPU issues fixed, count-agnostic commands.

## Rationale

CPU-side culling and draw submission scales linearly with object count and becomes the frame bottleneck in dense scenes. GPU-driven rendering inverts this: the CPU uploads persistent scene data once (transforms, bounds, mesh references), a compute pass culls and compacts visible instances into a draw-indirect buffer, and the graphics pass consumes that buffer with `DrawIndirect`/`DispatchIndirect`. The CPU never reads back the visible count. This is the architectural pattern behind Unreal Nanite's cluster culling, Unity BatchRendererGroup / GPU Resident Drawer, and modern mesh-shader pipelines — the names and APIs differ, but the model is: GPU decides what to draw, CPU submits one indirect command.

## How to Apply

1. **Persistent scene buffers** — Store per-instance data (transform, bounds, mesh/material indices) in GPU storage buffers updated incrementally, not re-uploaded wholesale each frame.
2. **GPU cull pass** — Compute shader tests each instance against frustum (and optionally Hi-Z); surviving instances append to a compact visible list via atomics or prefix sum.
3. **Fill indirect args** — A separate compute pass (or the cull pass tail) writes `DrawIndirectArguments` (vertex/index counts, instance count, offsets) into a GPU buffer.
4. **Indirect draw** — Bind the compact instance buffer and issue one or few `DrawIndexedIndirect` calls; instance count comes from the GPU-written buffer, not the CPU.
5. **Multi-pass reuse** — The same visible list can feed shadow, depth-prepass, and color passes if they share cull criteria; re-cull only when criteria differ.
6. **Mesh shaders (optional)** — Amplification/mesh shader stages can cull and emit triangles on-GPU without a separate compute compact pass; same goal, different pipeline stage.

## Example

```c
// GPU cull -> compact visible instances -> indirect draw. CPU issues fixed commands.
// (Neutral pseudocode; concrete API objects live in the per-API skill.)

// Persistent: instance buffer with bounds + mesh_id per instance.
// Per frame:
cmd_dispatch_compute(cmd, cull_cs, (groups_x, 1, 1));   // frustum test, atomic append to visible[]
cmd_dispatch_compute(cmd, fill_indirect_cs, (1, 1, 1)); // write DrawIndirectArguments from visible_count

cmd_bind_pipeline(cmd, depth_prepass_pso);
cmd_bind_vertex_buffer(cmd, compact_visible_instances);
cmd_draw_indexed_indirect(cmd, indirect_args_buffer, 0); // count from GPU, not CPU
```

## Gotchas

- Reading the visible count back to the CPU to size a loop defeats the purpose — the whole draw must be indirect.
- Atomic append without a max bound can overflow the compact buffer; size for worst case or use a two-pass prefix-sum compact.
- GPU cull and indirect draw in the same command buffer need a barrier between compute write and draw read of the indirect args buffer.
- Different passes (shadow vs color) may need different cull sets — sharing one visible list when shadow casters differ culls wrong objects.
- Mesh shader paths require API/hardware support; keep a compute-cull + traditional draw fallback for broader compatibility.
- Instance data in the compact buffer must match what the vertex shader expects — layout the cull output to match the draw shader's fetch path.

## Related

[references/gpu-compute-simulation.md](./gpu-compute-simulation.md), [references/scene-rendering-culling.md](./scene-rendering-culling.md), [references/binding-model.md](./binding-model.md), [references/synchronization.md](./synchronization.md)
