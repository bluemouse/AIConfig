# synchronization: VkSemaphore, VkFence, and Submit-Time Waits

## Guideline

Use the right Vulkan primitive for each relationship: pipeline barriers for in-queue hazards (covered in [resources-and-barriers.md](./resources-and-barriers.md)), binary `VkSemaphore` for queue->queue and swapchain ordering, timeline `VkSemaphore` for monotonic counter waits that the CPU can also wait on, and `VkFence` for GPU->CPU completion — wiring waits and signals through `VkSubmitInfo2`/`vkQueueSubmit2` scoped to exactly the work that must wait.

## Rationale

Vulkan orders nothing across submissions or queues unless you ask. A binary `VkSemaphore` is a GPU-side handoff: one `vkQueueSubmit2` signals it, the next waits on it — used for swapchain acquire->render->present and for async-compute handoff. A timeline `VkSemaphore` is a 64-bit counter: you wait for value >= N and signal value N, so one object expresses many dependencies, supports wait-before-signal, and `vkWaitSemaphores` lets the CPU wait too — often retiring per-frame fences. A `VkFence` is the only GPU->CPU signal: the CPU blocks in `vkWaitForFences` to know a frame slot's command buffers, descriptors, and ring ranges are free to reuse, or that readback has landed. With synchronization2, semaphore waits/signals carry a `stageMask` so the wait is scoped to the stage that actually depends. The agnostic model is in [gpu-rendering-guide synchronization](../../gpu-rendering-guide/references/synchronization.md).

## Techniques

- **Binary semaphore** - `vkCreateSemaphore` (no type info); signal in one submit's `pSignalSemaphoreInfos`, wait in the next's `pWaitSemaphoreInfos` with a `stageMask`. Used for swapchain image-available / render-finished.
- **Timeline semaphore** - `VkSemaphoreTypeCreateInfo{ VK_SEMAPHORE_TYPE_TIMELINE, initialValue }`; wait/signal a `value` via `VkSemaphoreSubmitInfo`; CPU side `vkWaitSemaphores`/`vkSignalSemaphore`/`vkGetSemaphoreCounterValue`. Requires the `timelineSemaphore` feature.
- **Fence** - `vkCreateFence` (create signaled for first-frame convenience); pass to `vkQueueSubmit2`; `vkWaitForFences` then `vkResetFences` to gate frame-slot reuse, see [commands-and-swapchain.md](./commands-and-swapchain.md).
- **Submit2** - `vkQueueSubmit2` with `VkSubmitInfo2{ pWaitSemaphoreInfos, pCommandBufferInfos, pSignalSemaphoreInfos }`; each semaphore info carries a `stageMask` (and a `value` if timeline).
- **Stage-scoped waits** - Set the wait `stageMask` to the consuming stage (e.g. `COLOR_ATTACHMENT_OUTPUT` waiting on image-available), not `ALL_COMMANDS`, so earlier stages overlap the wait.
- **No idle in the frame loop** - Retire frame resources by fence/timeline value; reserve `vkDeviceWaitIdle`/`vkQueueWaitIdle` for teardown, swapchain recreation, or one-off recovery.

## Example

```cpp
// Timeline semaphore: one monotonic counter for graphics->compute handoff + CPU wait.
VkSemaphoreTypeCreateInfo tci{
    .sType = VK_STRUCTURE_TYPE_SEMAPHORE_TYPE_CREATE_INFO,
    .semaphoreType = VK_SEMAPHORE_TYPE_TIMELINE, .initialValue = 0,
};
VkSemaphoreCreateInfo sci{.sType = VK_STRUCTURE_TYPE_SEMAPHORE_CREATE_INFO, .pNext = &tci};
VkSemaphore timeline = VK_NULL_HANDLE;
vkCreateSemaphore(dev, &sci, nullptr, &timeline);

VkSemaphoreSubmitInfo signal{
    .sType = VK_STRUCTURE_TYPE_SEMAPHORE_SUBMIT_INFO,
    .semaphore = timeline, .value = frameValue,
    .stageMask = VK_PIPELINE_STAGE_2_ALL_GRAPHICS_BIT,
};
VkCommandBufferSubmitInfo cbi{.sType = VK_STRUCTURE_TYPE_COMMAND_BUFFER_SUBMIT_INFO, .commandBuffer = cmd};
VkSubmitInfo2 si{
    .sType = VK_STRUCTURE_TYPE_SUBMIT_INFO_2,
    .commandBufferInfoCount = 1, .pCommandBufferInfos = &cbi,
    .signalSemaphoreInfoCount = 1, .pSignalSemaphoreInfos = &signal,
};
vkQueueSubmit2(gfxQueue, 1, &si, frameFence);                    // fence: GPU->CPU reuse gate

// CPU can wait on the timeline value directly (often instead of a fence).
VkSemaphoreWaitInfo wi{
    .sType = VK_STRUCTURE_TYPE_SEMAPHORE_WAIT_INFO,
    .semaphoreCount = 1, .pSemaphores = &timeline, .pValues = &frameValue,
};
vkWaitSemaphores(dev, &wi, UINT64_MAX);
```

## Gotchas

- A binary `VkSemaphore` must be waited exactly once per signal; signaling one already pending-signal (or waiting an unsignaled one with nothing to signal it) deadlocks.
- A wait `stageMask` of `ALL_COMMANDS` defeats overlap — scope it to the consuming stage (e.g. image-available waited at `COLOR_ATTACHMENT_OUTPUT`).
- Semaphores order GPU work but do not perform the memory availability/visibility a barrier does within a queue — you still need barriers at a queue boundary, see [resources-and-barriers.md](./resources-and-barriers.md).
- `vkWaitForFences` on the frame you just submitted (instead of the slot you are about to reuse) collapses frames-in-flight into a full stall.
- A timeline value must only increase; signaling a value <= the current counter is invalid.

## Related

[resources-and-barriers.md](./resources-and-barriers.md), [commands-and-swapchain.md](./commands-and-swapchain.md), [device-and-queues.md](./device-and-queues.md)
