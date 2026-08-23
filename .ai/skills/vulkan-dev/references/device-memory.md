# device-memory: VkDeviceMemory, Memory Types, and Staging

## Guideline

Query `VkPhysicalDeviceMemoryProperties`, allocate a few large `VkDeviceMemory` blocks of the right memory type, and sub-allocate every `VkImage`/`VkBuffer` out of them honoring `VkMemoryRequirements.alignment`; upload static data via a `HOST_VISIBLE` staging buffer copied with `vkCmdCopyBuffer`/`vkCmdCopyBufferToImage` into a `DEVICE_LOCAL` resource; persistently map host-visible blocks. Never call `vkAllocateMemory` per resource.

## Rationale

Vulkan exposes memory as types (each a heap + property-flag combination) you select explicitly; the driver does not place resources for you. `vkAllocateMemory` count is capped by `maxMemoryAllocationCount` (often ~4096) and each call is slow, so one allocation per resource fails at scale — sub-allocate from large blocks instead. The CPU-side bookkeeping is the same arena/pool principle described in [cpp-memory-guide](../../cpp-memory-guide/SKILL.md); the GPU-side strategy (tiers, staging, rings, defrag) is in [gpu-rendering-guide gpu-memory-strategy](../../gpu-rendering-guide/references/gpu-memory-strategy.md). `DEVICE_LOCAL` memory is the fast GPU path but usually lacks `HOST_VISIBLE`, so the CPU cannot write it directly; static data is therefore written into a `HOST_VISIBLE | HOST_COHERENT` staging buffer and copied on a queue into the device-local resource. Each `VkImage`/`VkBuffer` reports its own `VkMemoryRequirements` (size, alignment, allowed `memoryTypeBits`); placement must satisfy that alignment, and buffer<->image co-placement must respect `bufferImageGranularity`.

## Techniques

- **Memory type selection** - Scan `VkPhysicalDeviceMemoryProperties.memoryTypes`; require the resource's `memoryTypeBits` and the property flags you want (`DEVICE_LOCAL`; `HOST_VISIBLE | HOST_COHERENT`; `DEVICE_LOCAL | HOST_VISIBLE` for resizable-BAR direct writes).
- **Few large blocks** - `vkAllocateMemory` a 64-256 MB block per type; sub-allocate with a block/free-list allocator so call sites request `(size, usage)`.
- **Alignment** - Use `vkGetBufferMemoryRequirements2` / `vkGetImageMemoryRequirements2`; align the sub-allocation offset to `req.alignment` and keep buffers/images apart by `bufferImageGranularity`.
- **Staging upload** - Map a `HOST_VISIBLE` staging buffer, `memcpy`, `vkCmdCopyBufferToImage` / `vkCmdCopyBuffer` into the `DEVICE_LOCAL` target, then a barrier to the read state, see [resources-and-barriers.md](./resources-and-barriers.md).
- **Persistent mapping** - `vkMapMemory` a host-visible block once and keep the pointer; without `HOST_COHERENT`, `vkFlushMappedMemoryRanges` after writes and `vkInvalidateMappedMemoryRanges` before reads (align ranges to `nonCoherentAtomSize`).
- **Real allocator** - Use Vulkan Memory Allocator (VMA) or an equivalent engine allocator over these techniques (block management, type selection, defrag) unless you are explicitly implementing the allocator; call sites never touch raw `VkDeviceMemory`.
- **Block strategy by size** - A workable split: device-local requests <= a block size (e.g. 256 MB) sub-allocate from buddy-managed 256 MB blocks; larger requests get a dedicated `vkAllocateMemory`; staging uses a linear allocator over `max(size, 256 MB)` blocks recycled once the transfer fence signals.
- **Tagged visual debugging** - Pass a debug tag with every allocation and build a simple occupancy visualization early; buddy power-of-two rounding waste and never-released empty blocks are invisible otherwise.
- **Budget** - Track `VK_EXT_memory_budget` where available and avoid surprise overcommit.

## Example

```cpp
VkPhysicalDeviceMemoryProperties mp;
vkGetPhysicalDeviceMemoryProperties(phys, &mp);

auto pickType = [&](uint32_t typeBits, VkMemoryPropertyFlags want) -> uint32_t {
    for (uint32_t i = 0; i < mp.memoryTypeCount; i++)
        if ((typeBits & (1u << i)) &&
            (mp.memoryTypes[i].propertyFlags & want) == want) return i;
    return UINT32_MAX;
};

VkMemoryRequirements req;
vkGetImageMemoryRequirements(dev, image, &req);
GpuAlloc a = blockAlloc(allocator, req.size, req.alignment,          // sub-allocate, honor alignment
    pickType(req.memoryTypeBits, VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT));
vkBindImageMemory(dev, image, a.memory, a.offset);

// Static upload: HOST_VISIBLE staging -> DEVICE_LOCAL via a copy on the queue.
void* dst = nullptr;
vkMapMemory(dev, stage.memory, stage.offset, size, 0, &dst);
memcpy(dst, pixels, size);
VkBufferImageCopy region{
    .imageSubresource = {VK_IMAGE_ASPECT_COLOR_BIT, 0, 0, 1},
    .imageExtent = {w, h, 1},
};
vkCmdCopyBufferToImage(cmd, stage.buffer, image,
                       VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL, 1, &region);
```

## Gotchas

- `maxMemoryAllocationCount` is small; per-resource `vkAllocateMemory` works in a demo then fails in a real scene — sub-allocate from the start.
- `DEVICE_LOCAL`-only memory has no host pointer; `vkMapMemory` on it fails — write through staging.
- Without `HOST_COHERENT`, a written-but-unflushed range is not visible to the GPU; coherent memory skips flush/invalidate but can be slower for the GPU to read.
- Ignoring `req.alignment` or `bufferImageGranularity` produces a valid bind that corrupts neighboring resources on some hardware.
- A staging buffer reused before its copy's fence signals overwrites in-flight upload data — recycle staging by frame fence, see [commands-and-swapchain.md](./commands-and-swapchain.md).
- Do not assume host-visible memory is fast for GPU reads; on discrete GPUs prefer device-local + staging unless a measured UMA/resizable-BAR path wins.

## Related

[resources-and-barriers.md](./resources-and-barriers.md), [commands-and-swapchain.md](./commands-and-swapchain.md), [synchronization.md](./synchronization.md), [gpu-rendering-guide gpu-memory-strategy](../../gpu-rendering-guide/references/gpu-memory-strategy.md)
