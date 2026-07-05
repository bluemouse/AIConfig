# compute: Compute Pipelines, Dispatch, Workgroups, and Subgroups

Use this reference for compute pipelines, GPU data processing, reductions, image compute, async compute, and GPU-driven work. For the agnostic GPU-simulation and GPU-driven-rendering architecture, see [gpu-rendering-guide gpu-compute-simulation](../../gpu-rendering-guide/references/gpu-compute-simulation.md) and [gpu-driven-rendering](../../gpu-rendering-guide/references/gpu-driven-rendering.md).

## Compute setup checklist

- Verify a queue family with `VK_QUEUE_COMPUTE_BIT`. A graphics queue often also supports compute; a dedicated compute queue is optional.
- Create pipelines with `vkCreateComputePipelines` (cache-backed, see [pipelines.md](./pipelines.md)); bind with `VK_PIPELINE_BIND_POINT_COMPUTE`.
- Dispatch with `vkCmdDispatch`, `vkCmdDispatchIndirect`, or device-generated paths only when supported.
- Bind descriptors/push constants compatible with the compute pipeline layout, see [descriptors.md](./descriptors.md).
- Insert barriers between producer and consumer dispatches, transfers, graphics passes, or host reads, see [resources-and-barriers.md](./resources-and-barriers.md).

## Workgroup sizing

Check device limits and shader assumptions before hardcoding a local size:

- `maxComputeWorkGroupInvocations`.
- `maxComputeWorkGroupSize[0..2]`.
- `maxComputeWorkGroupCount[0..2]`.
- Subgroup size/properties if subgroup operations are used.
- Shared-memory limits.

Do not hardcode one local size for every GPU. Use specialization constants or multiple pipelines if workgroup size is a tuning parameter.

## Dispatch sizing

For N elements and local size L:

```cpp
uint32_t groupCount = (N + L - 1) / L;
vkCmdDispatch(cmd, groupCount, 1, 1);
```

Guard out-of-range invocations in the shader:

```glsl
uint i = gl_GlobalInvocationID.x;
if (i >= elementCount) { return; }
```

## Storage buffers and images

- Prefer SSBOs for linear/structured data; use storage images when 2D/3D locality or image-format behavior is needed.
- Check storage-image format-feature support before use, see [capabilities-and-setup.md](./capabilities-and-setup.md).
- For host readback, copy to a host-visible readback buffer and synchronize GPU writes before mapping/reading.
- For non-coherent memory, flush/invalidate aligned ranges (`nonCoherentAtomSize`).

## Compute synchronization examples

Compute write -> compute read (memory barrier):

```cpp
VkMemoryBarrier2 barrier{
    .sType = VK_STRUCTURE_TYPE_MEMORY_BARRIER_2,
    .srcStageMask = VK_PIPELINE_STAGE_2_COMPUTE_SHADER_BIT,
    .srcAccessMask = VK_ACCESS_2_SHADER_WRITE_BIT,
    .dstStageMask = VK_PIPELINE_STAGE_2_COMPUTE_SHADER_BIT,
    .dstAccessMask = VK_ACCESS_2_SHADER_READ_BIT,
};
VkDependencyInfo dep{
    .sType = VK_STRUCTURE_TYPE_DEPENDENCY_INFO,
    .memoryBarrierCount = 1, .pMemoryBarriers = &barrier,
};
vkCmdPipelineBarrier2(cmd, &dep);
```

Compute write -> transfer read (buffer barrier):

```cpp
VkBufferMemoryBarrier2 barrier{
    .sType = VK_STRUCTURE_TYPE_BUFFER_MEMORY_BARRIER_2,
    .srcStageMask = VK_PIPELINE_STAGE_2_COMPUTE_SHADER_BIT,
    .srcAccessMask = VK_ACCESS_2_SHADER_WRITE_BIT,
    .dstStageMask = VK_PIPELINE_STAGE_2_COPY_BIT,
    .dstAccessMask = VK_ACCESS_2_TRANSFER_READ_BIT,
    .buffer = buffer, .offset = 0, .size = VK_WHOLE_SIZE,
};
VkDependencyInfo dep{
    .sType = VK_STRUCTURE_TYPE_DEPENDENCY_INFO,
    .bufferMemoryBarrierCount = 1, .pBufferMemoryBarriers = &barrier,
};
vkCmdPipelineBarrier2(cmd, &dep);
```

Compute write -> graphics shader read: `dstStageMask = VK_PIPELINE_STAGE_2_VERTEX_SHADER_BIT | VK_PIPELINE_STAGE_2_FRAGMENT_SHADER_BIT`, `dstAccessMask = VK_ACCESS_2_SHADER_READ_BIT`.

## Subgroups

- Query subgroup properties before relying on subgroup size or supported operations.
- Do not assume warp/wave size is 32 or 64.
- Use subgroup operations for reductions/scans only when supported and measured beneficial; provide a non-subgroup fallback for broad portability unless the target is constrained.

## Async compute

Async compute is worthwhile only when all hold:

- A queue family/topology can run compute concurrently with graphics.
- The workload is large enough to hide synchronization overhead.
- Resources and barriers do not immediately serialize the graphics queue.
- GPU profiling shows real overlap and improved frame time.

Do not move compute to an async queue as a default — many workloads perform better on the graphics queue due to locality and lower sync cost. Async handoff uses semaphores + queue-family ownership transfer, see [synchronization.md](./synchronization.md) and [resources-and-barriers.md](./resources-and-barriers.md).

## GPU-compute kernels

- Batch memory reads/writes and minimize global-memory traffic.
- Use shared memory only when it reduces real bandwidth and avoids bank conflicts on target hardware.
- Specialize layouts and workgroup sizes per operator shape when possible.
- Prefer fp16/int8 paths only when device features, shader capabilities, precision requirements, and memory layout are verified.
- Keep descriptor and pipeline permutations manageable.

## Related

[pipelines.md](./pipelines.md), [descriptors.md](./descriptors.md), [resources-and-barriers.md](./resources-and-barriers.md), [synchronization.md](./synchronization.md), [capabilities-and-setup.md](./capabilities-and-setup.md)
