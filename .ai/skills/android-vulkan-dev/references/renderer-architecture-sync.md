# Renderer architecture and Android lifecycle

## Use this file when

Use this reference when designing the Android renderer shape, handling surface resize/pause/rotation/device-lost, or structuring painting/photo GPU pipelines on Android.

For generic Vulkan synchronization, frames-in-flight, barriers, memory, and pipeline rules, use [vulkan-dev](../../vulkan-dev/SKILL.md). For API-agnostic render-graph architecture, use [gpu-rendering-guide](../../gpu-rendering-guide/SKILL.md).

## Object model (Android layer)

Split Android-specific ownership from generic Vulkan subsystems:

```text
VulkanRendererHost (Kotlin)     Surface lifecycle, attach/resize/close
Renderer (C++)
  SurfaceContext                ANativeWindow, VkSurfaceKHR
  Swapchain                     WSI images, format, transform, recreation
  AppRenderer                   delegates to vulkan-dev subsystems:
    DeviceContext               instance, device, queues (vulkan-dev)
    ResourceAllocator           buffers, images, memory (vulkan-dev)
    PipelineLibrary             shaders, pipelines, cache (vulkan-dev)
    FrameScheduler              fences, semaphores, command buffers (vulkan-dev)
  Document/Scene                app draw/filter commands
```

Prefer Vulkan 1.3 modern path from [vulkan-dev](../../vulkan-dev/SKILL.md): dynamic rendering (`vkCmdBeginRendering`), synchronization2 (`vkCmdPipelineBarrier2`, `vkQueueSubmit2`), timeline semaphores, descriptor indexing where supported.

## Android lifecycle and resize

Swapchain recreation must not leak old resources or block forever.

1. Stop submitting new frames when `Surface` is destroyed or app pauses.
2. Wait for per-frame fences or retire in-flight frames using old swapchain images.
3. Destroy swapchain-dependent resources (image views, depth targets).
4. Query surface capabilities again (size, transform, format may have changed).
5. Recreate swapchain and dependent targets.
6. Resume rendering.

Handle `VK_ERROR_OUT_OF_DATE_KHR` and `VK_SUBOPTIMAL_KHR` from acquire/present by recreating the swapchain. See [vulkan-dev](../../vulkan-dev/references/commands-and-swapchain.md).

On device lost, assume most Vulkan objects are invalid. Recreate the renderer from a clean state or surface a fatal unsupported error.

## Display rotation

Apply `VkSurfaceCapabilitiesKHR::currentTransform` during rendering and set swapchain `preTransform` appropriately. Rendering with the wrong transform forces compositor rotation and wastes bandwidth on tile-based mobile GPUs.

## Painting and image editor architecture

For painting/photo apps on Android:

```text
Document model: layers, masks, strokes, adjustments, metadata (CPU/Kotlin)
GPU resources: tiled textures, intermediate targets, brush atlases, LUTs
Renderer commands: draw stroke, composite layer, apply preview filter, export tile
CPU side: history, file IO, thumbnails, metadata, scheduling (android-dev)
```

Rules:

- Use tiles for very large canvases or images.
- Keep brush stroke input in a low-latency queue.
- Render preview at screen resolution; export at full resolution on a background worker.
- Bound undo/redo memory. Store commands and changed tiles, not full copies per edit.
- Hand off camera/media buffers per [camera-media-image-interop.md](camera-media-image-interop.md).

## Mobile GPU bandwidth

Android devices often use tile-based mobile GPUs. Minimize render passes and external memory bandwidth. Prefer combined passes and transient attachments. Avoid full-screen intermediate copies unless required. See [vulkan-dev](../../vulkan-dev/references/best-practices.md) for mobile tiler guidance.

## Common Android-specific bugs

- Rendering after `Surface` is destroyed (common on background/foreground transitions).
- Black frame after resize because old swapchain images were used.
- Ignoring surface transform on rotation.
- Importing camera/media buffers without correct external synchronization.
- Blocking camera acquisition while waiting for GPU work on the UI thread.

For generic sync bugs (layout transitions, fence reuse, deferred deletion), see [vulkan-dev](../../vulkan-dev/references/synchronization.md) and [vulkan-dev](../../vulkan-dev/references/resources-and-barriers.md).
