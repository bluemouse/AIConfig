# commands-and-swapchain: VkCommandPool, Command Buffers, and the Swapchain

## Guideline

Allocate command buffers from one `VkCommandPool` per recording thread per frame slot and reset the whole pool with `vkResetCommandPool` once the slot's `VkFence` signals; record independent passes into secondary `VkCommandBuffer`s executed by a primary; drive presentation with `vkAcquireNextImageKHR`/`vkQueuePresentKHR` over a `VkSwapchainKHR`, keeping N frame slots in flight each with its own pools, per-frame resources, and a fence.

## Rationale

A `VkCommandPool` is externally synchronized and frees buffers cheaply only as a whole (`vkResetCommandPool` / `vkResetCommandBuffer`), so the efficient model is one pool per (thread x frame slot): record, submit, and later reset the whole pool in O(1) once the GPU is done — proven done by the slot's `VkFence`. Keeping 2-3 frame slots in flight lets the CPU record slot i while the GPU runs slot i-1. Recording parallelizes: worker threads each fill a secondary `VkCommandBuffer` from their own pool, and a primary buffer runs them with `vkCmdExecuteCommands`. The swapchain ties it together — `vkAcquireNextImageKHR` returns an image index and signals an image-available semaphore, you render into that image, then `vkQueuePresentKHR` waits the render-finished semaphore. The agnostic frames-in-flight model is in [gpu-rendering-guide command-recording-and-frames](../../gpu-rendering-guide/references/command-recording-and-frames.md).

## Techniques

- **Pool per thread per frame** - `vkCreateCommandPool` per (recording thread x frame slot); `vkResetCommandPool` when the slot fence signals; never `vkFreeCommandBuffers` per buffer on the hot path.
- **One-time submit** - Record one-frame buffers with `VK_COMMAND_BUFFER_USAGE_ONE_TIME_SUBMIT_BIT`; avoid `SIMULTANEOUS_USE_BIT` unless genuinely needed.
- **Primary/secondary** - Primary buffers go to `vkQueueSubmit2`; secondaries are recorded with `VkCommandBufferInheritanceInfo` and invoked via `vkCmdExecuteCommands`. Give each secondary enough work to amortize its overhead.
- **Frames in flight** - N slots (2-3), each owning command pools, per-frame descriptor sets, ring-buffer ranges, image-available/render-finished semaphores, and one `VkFence`.
- **Swapchain creation** - `vkCreateSwapchainKHR` from surface caps/formats/present modes; retrieve images with `vkGetSwapchainImagesKHR`; create a `VkImageView` per image.
- **Acquire/submit/present** - `vkAcquireNextImageKHR` (signal image-available) -> record -> `vkQueueSubmit2` (wait image-available, signal render-finished, signal fence) -> `vkQueuePresentKHR` (wait render-finished), see [synchronization.md](./synchronization.md).
- **Recreation** - On `VK_ERROR_OUT_OF_DATE_KHR`/`VK_SUBOPTIMAL_KHR` or resize, `vkDeviceWaitIdle`, destroy, and recreate the swapchain and its views/targets.
- **Fence-gated deletion + pool recycling** - Attach a queue of pending resource destroys to each submission; process them (and reset/recycle the slot's command and descriptor pools into a free "pool of pools") only when the slot's `VkFence` signals. Recycling whole pools keeps reuse O(1) and avoids fragmentation.

## Example

```cpp
enum { FRAMES_IN_FLIGHT = 2 };
struct FrameSlot {
    VkCommandPool   pool;            // reset wholesale, not per-buffer
    VkCommandBuffer cmd;
    VkFence         inFlight;        // signaled when this slot's GPU work completes
    VkSemaphore     imageAvailable, renderFinished;
};
FrameSlot slots[FRAMES_IN_FLIGHT];

void drawFrame(uint64_t frame) {
    FrameSlot& s = slots[frame % FRAMES_IN_FLIGHT];
    vkWaitForFences(dev, 1, &s.inFlight, VK_TRUE, UINT64_MAX); // wait the slot we reuse
    vkResetFences(dev, 1, &s.inFlight);

    uint32_t img = 0;
    VkResult r = vkAcquireNextImageKHR(dev, swapchain, UINT64_MAX, s.imageAvailable, VK_NULL_HANDLE, &img);
    if (r == VK_ERROR_OUT_OF_DATE_KHR) { recreateSwapchain(); return; }

    vkResetCommandPool(dev, s.pool, 0);                        // O(1); fence guarantees safe
    VkCommandBufferBeginInfo begin{
        .sType = VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO,
        .flags = VK_COMMAND_BUFFER_USAGE_ONE_TIME_SUBMIT_BIT,
    };
    vkBeginCommandBuffer(s.cmd, &begin);
    vkCmdExecuteCommands(s.cmd, nWorkers, secondaries);        // workers filled these
    vkEndCommandBuffer(s.cmd);

    VkSemaphoreSubmitInfo wait{
        .sType = VK_STRUCTURE_TYPE_SEMAPHORE_SUBMIT_INFO, .semaphore = s.imageAvailable,
        .stageMask = VK_PIPELINE_STAGE_2_COLOR_ATTACHMENT_OUTPUT_BIT,
    };
    VkSemaphoreSubmitInfo sig{
        .sType = VK_STRUCTURE_TYPE_SEMAPHORE_SUBMIT_INFO, .semaphore = s.renderFinished,
        .stageMask = VK_PIPELINE_STAGE_2_ALL_GRAPHICS_BIT,
    };
    VkCommandBufferSubmitInfo cbi{.sType = VK_STRUCTURE_TYPE_COMMAND_BUFFER_SUBMIT_INFO, .commandBuffer = s.cmd};
    VkSubmitInfo2 si{
        .sType = VK_STRUCTURE_TYPE_SUBMIT_INFO_2,
        .waitSemaphoreInfoCount = 1, .pWaitSemaphoreInfos = &wait,
        .commandBufferInfoCount = 1, .pCommandBufferInfos = &cbi,
        .signalSemaphoreInfoCount = 1, .pSignalSemaphoreInfos = &sig,
    };
    vkQueueSubmit2(gfxQueue, 1, &si, s.inFlight);              // fence signals on completion
    VkPresentInfoKHR present{
        .sType = VK_STRUCTURE_TYPE_PRESENT_INFO_KHR,
        .waitSemaphoreCount = 1, .pWaitSemaphores = &s.renderFinished,
        .swapchainCount = 1, .pSwapchains = &swapchain, .pImageIndices = &img,
    };
    vkQueuePresentKHR(presentQueue, &present);
}
```

## Gotchas

- Resetting a pool or recording into a buffer whose previous submission's fence has not signaled corrupts in-flight GPU work — always gate on the slot fence.
- A `VkCommandPool` is not thread-safe; two threads recording from one pool race — one pool per thread.
- Waiting on the fence you just submitted (not the slot about to be reused) collapses frames-in-flight into a stall.
- Ignoring `VK_SUBOPTIMAL_KHR`/`VK_ERROR_OUT_OF_DATE_KHR` from acquire or present leaves a stale swapchain after resize — recreate it (and never present into a stale image).
- The image-available semaphore must be one not currently pending on another acquire; using a per-frame-slot semaphore avoids reusing one mid-flight.

## Related

[synchronization.md](./synchronization.md), [device-memory.md](./device-memory.md), [resources-and-barriers.md](./resources-and-barriers.md), [device-and-queues.md](./device-and-queues.md)
