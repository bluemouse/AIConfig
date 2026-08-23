# capabilities-and-setup: Version Policy, Feature/Extension Detection, Instance & WSI

Use this reference when creating or modernizing Vulkan setup, choosing what to target, probing device capability, or designing fallback tiers. For the concrete `VkInstance`/`VkDevice`/queue object-creation code, see [device-and-queues.md](./device-and-queues.md).

## Version policy

- Target **Vulkan 1.3** by default; require `apiVersion >= VK_API_VERSION_1_3` for the modern path.
- Use Vulkan 1.3 core struct/function names when the app selected a 1.3 device path.
- Use extension names/functions only for compatibility paths targeting older versions, or for functionality not promoted to core.
- Never assume optional features because headers expose the symbols. Header availability is not runtime support — query and enable features at `VkDevice` creation.
- Do not invent extension promotion status, mandatory limits, or exact function signatures; when exact spec wording matters, consult the spec, see [code-review-and-audit.md](./code-review-and-audit.md).

## Core rules for capability handling

- Query before enabling; enable before using.
- Distinguish instance extensions from device extensions.
- Distinguish extension availability from feature-bit availability.
- Distinguish API-version promotion from enabled functionality.
- Keep the required-feature set minimal and explicit.

Using extension functionality without enabling the required extension for the selected path is undefined/invalid.

## Feature groups (Vulkan 1.1/1.2/1.3)

- `VkPhysicalDeviceVulkan11Features`: shader draw parameters and 1.1 controls.
- `VkPhysicalDeviceVulkan12Features`: timeline semaphores, descriptor indexing, buffer device address, scalar block layout, host query reset, separate depth/stencil layouts, draw-indirect count, runtime descriptor arrays, partially bound descriptors, update-after-bind.
- `VkPhysicalDeviceVulkan13Features`: synchronization2, dynamic rendering, maintenance4, shader demote-to-helper, shader integer dot product, pipeline creation cache control, private data.

Only enable features the code actually uses. Treat optional performance features as tier upgrades, not baseline requirements unless the user targets a controlled platform.

## Feature-query and device-creation pattern

Query with one pNext chain, then reuse a sanitized enable chain that sets only required bits.

```cpp
VkPhysicalDeviceVulkan13Features f13{.sType = VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_VULKAN_1_3_FEATURES};
VkPhysicalDeviceVulkan12Features f12{.sType = VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_VULKAN_1_2_FEATURES, .pNext = &f13};
VkPhysicalDeviceVulkan11Features f11{.sType = VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_VULKAN_1_1_FEATURES, .pNext = &f12};
VkPhysicalDeviceFeatures2 features2{.sType = VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_FEATURES_2, .pNext = &f11};
vkGetPhysicalDeviceFeatures2(physicalDevice, &features2);

if (!f13.synchronization2 || !f13.dynamicRendering || !f12.timelineSemaphore) {
    // Reject the modern path or select a fallback backend.
}

// Second chain: enable ONLY the required bits.
VkPhysicalDeviceVulkan13Features enable13{
    .sType = VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_VULKAN_1_3_FEATURES,
    .synchronization2 = VK_TRUE, .dynamicRendering = VK_TRUE,
};
VkPhysicalDeviceVulkan12Features enable12{
    .sType = VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_VULKAN_1_2_FEATURES,
    .pNext = &enable13, .timelineSemaphore = VK_TRUE,
};
VkPhysicalDeviceFeatures2 enableFeatures{
    .sType = VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_FEATURES_2, .pNext = &enable12,
};
// pass &enableFeatures as VkDeviceCreateInfo::pNext
```

Do not pass unsupported bits set to `VK_TRUE`, and do not blindly copy the queried struct into device creation — enabling unused bits complicates portability and audits. Keep the pNext storage alive until the create/query call returns.

## Two-phase enumeration

Use the two-call size-then-fill pattern for instance/device extensions, layers, physical devices, queue families, formats, present modes, and memory budget.

```cpp
std::vector<VkExtensionProperties> enumerateDeviceExtensions(VkPhysicalDevice dev) {
    uint32_t count = 0;
    vkEnumerateDeviceExtensionProperties(dev, nullptr, &count, nullptr);
    std::vector<VkExtensionProperties> props(count);
    vkEnumerateDeviceExtensionProperties(dev, nullptr, &count, props.data());
    return props;
}
bool hasExtension(std::span<const VkExtensionProperties> props, const char* name) {
    return std::any_of(props.begin(), props.end(),
        [&](const auto& p) { return std::strcmp(p.extensionName, name) == 0; });
}
```

Produce three feature sets when generating detection code: `Available` (queried), `Required` (must be true for the backend), `Enabled` (only required/used bits true).

## Instance setup

- Enable validation layers only when available and only in development/debug builds.
- Use `VK_EXT_debug_utils` for object names, labels, and a debug messenger when available; name objects early (maintainability).
- Enumerate instance extensions before enabling; WSI/platform extensions come from the windowing layer exactly as required.
- On portability platforms (macOS via MoltenVK), gate `VK_KHR_portability_enumeration` / `VK_KHR_portability_subset` deliberately.

## Physical-device selection

Reject first on required correctness capabilities, then rank on preference:

1. Vulkan 1.3 support.
2. Required queue capabilities: graphics, compute, transfer, present for the chosen surface.
3. Required features and extensions.
4. Required formats and present modes.
5. Limits sufficient for descriptor counts, workgroup sizes, image dimensions, push constants, alignment, memory budget.
6. Device type and performance preference.

Do not auto-pick a discrete GPU that lacks required WSI, memory, feature, or format support.

## Optional feature tiers

- **required 1.3 path**: synchronization2, dynamic rendering, timeline semaphores, required WSI, required image/format capabilities.
- **modern descriptor tier**: runtime descriptor arrays, partially bound, update-after-bind, variable descriptor count.
- **gpu-driven tier**: buffer device address, draw-indirect count, mesh/task or device-generated commands only when explicitly supported.
- **compute tier**: storage buffer/image formats, subgroup requirements, workgroup limits, async compute only when queue topology supports it.
- **debug tier**: debug utils, validation layers, portability diagnostics.

## Extension dependency handling

Before enabling an extension: confirm instance vs device scope, dependencies, whether a feature bit must be enabled, whether new limits/properties must be queried, and whether it affects SPIR-V capabilities / shader compilation. Use a dispatch abstraction so core and extension entry points are never mixed inconsistently.

## Format feature detection

Check the corresponding `VkFormatProperties` feature bits before using a format in a role — color attachment, depth/stencil, storage image, sampled + linear filtering, blit/copy, atomics. Do not assume a format supports storage or linear filtering just because it supports sampling.

## WSI policy

- Swapchain acquire/present commonly uses binary semaphores; do not assume every WSI path can use timeline semaphores directly.
- Handle `VK_ERROR_OUT_OF_DATE_KHR` and `VK_SUBOPTIMAL_KHR` at acquire/present boundaries.
- Prefer per-frame fences + resource retirement over frame-loop `vkDeviceWaitIdle`; a coarse idle is acceptable for simple apps or one-off recovery/resize.
- Recreate swapchain-dependent images, views, rendering targets, and format-dependent pipelines only when required.

## Dynamic rendering default

For new 1.3 render paths use dynamic rendering when it simplifies pipeline/render-target management: `VkPipelineRenderingCreateInfo` in the pNext chain, `vkCmdBeginRendering` with explicit load/store ops and layouts. Preserve render-pass/subpass alternatives where tile-based architectures benefit, see [pipelines.md](./pipelines.md) and [best-practices.md](./best-practices.md).

## Error handling

- Check every `VkResult` that can fail; treat `VK_ERROR_DEVICE_LOST` as fatal requiring controlled teardown/recovery.
- Do not ignore allocation failures, swapchain status, pipeline creation errors, or shader-module failures.

## Related

[device-and-queues.md](./device-and-queues.md), [best-practices.md](./best-practices.md), [code-review-and-audit.md](./code-review-and-audit.md), [compute.md](./compute.md)
