# device-and-queues: Instance, Device, and Queue Families

## Guideline

Create a `VkInstance`, select a `VkPhysicalDevice`, create a logical `VkDevice` with the queues you need, and pick queue families by capability — a graphics family, and where the hardware exposes them a dedicated async-compute and a dedicated transfer family — requesting only the features/extensions you use. For the version policy, the `VkPhysicalDeviceFeatures2` query/enable chain, physical-device ranking, and extension enumeration, see [capabilities-and-setup.md](./capabilities-and-setup.md).

## Rationale

Vulkan has no implicit context: every object hangs off a `VkDevice`, which is created from a chosen `VkPhysicalDevice`, which is enumerated from the `VkInstance`. Queue families are how the hardware advertises which engines can run which work; a family with `VK_QUEUE_GRAPHICS_BIT` can do everything, but a dedicated `VK_QUEUE_TRANSFER_BIT`-only family runs DMA copies on a separate engine that overlaps graphics, and a compute-only family enables async compute that overlaps the graphics pipeline. You must request queues at device-creation time (you cannot add them later), and you must enable features (`VkPhysicalDeviceFeatures2` chain) and extensions explicitly. The architecture reason for owning all of this — the app owns memory, synchronization, and pipeline state — is in [gpu-rendering-guide](../../gpu-rendering-guide/SKILL.md).

## How to Apply

1. Create the `VkInstance` with required instance extensions (surface, plus debug-utils in development) and validation layers when developing.
2. Enumerate physical devices (`vkEnumeratePhysicalDevices`); pick one that supports your surface and required features (ranking in [capabilities-and-setup.md](./capabilities-and-setup.md)).
3. Query queue families (`vkGetPhysicalDeviceQueueFamilyProperties`); choose a graphics family that also supports present (`vkGetPhysicalDeviceSurfaceSupportKHR`), and dedicated compute/transfer families when present.
4. Create the `VkDevice` with `VkDeviceQueueCreateInfo` per family, chaining the `VkPhysicalDeviceFeatures2` / `*Vulkan13Features` you enable; retrieve queues with `vkGetDeviceQueue`.

## Example

```cpp
uint32_t n = 0;
vkGetPhysicalDeviceQueueFamilyProperties(phys, &n, nullptr);
std::vector<VkQueueFamilyProperties> props(n);
vkGetPhysicalDeviceQueueFamilyProperties(phys, &n, props.data());

uint32_t gfx = UINT32_MAX, xfer = UINT32_MAX;
for (uint32_t i = 0; i < n; i++) {
    if (props[i].queueFlags & VK_QUEUE_GRAPHICS_BIT) gfx = i;
    // dedicated transfer = TRANSFER but not GRAPHICS/COMPUTE -> separate DMA engine
    if ((props[i].queueFlags & VK_QUEUE_TRANSFER_BIT) &&
        !(props[i].queueFlags & (VK_QUEUE_GRAPHICS_BIT | VK_QUEUE_COMPUTE_BIT))) xfer = i;
}

float prio = 1.0f;
VkDeviceQueueCreateInfo qci{
    .sType = VK_STRUCTURE_TYPE_DEVICE_QUEUE_CREATE_INFO,
    .queueFamilyIndex = gfx, .queueCount = 1, .pQueuePriorities = &prio,
};
VkPhysicalDeviceVulkan13Features v13{
    .sType = VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_VULKAN_1_3_FEATURES,
    .synchronization2 = VK_TRUE, .dynamicRendering = VK_TRUE,
};
VkPhysicalDeviceFeatures2 features2{
    .sType = VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_FEATURES_2, .pNext = &v13,
};
VkDeviceCreateInfo dci{
    .sType = VK_STRUCTURE_TYPE_DEVICE_CREATE_INFO, .pNext = &features2,
    .queueCreateInfoCount = 1, .pQueueCreateInfos = &qci,
    .enabledExtensionCount = extCount, .ppEnabledExtensionNames = exts,
};
VkDevice dev = VK_NULL_HANDLE;
vkCreateDevice(phys, &dci, nullptr, &dev);
VkQueue gfxQueue = VK_NULL_HANDLE;
vkGetDeviceQueue(dev, gfx, 0, &gfxQueue);
```

## Gotchas

- A queue family that reports `GRAPHICS` may be the only one; do not assume a dedicated transfer/compute family exists — fall back to the graphics family.
- Present support is per (family x surface), not a device-wide property — query it with `vkGetPhysicalDeviceSurfaceSupportKHR`, and the present family may differ from graphics.
- Features must be enabled at device creation; using `descriptorIndexing` or `timelineSemaphore` without enabling it is undefined and validation-flagged.
- A resource used on two different queue families needs an ownership transfer, see [resources-and-barriers.md](./resources-and-barriers.md).

## Related

[capabilities-and-setup.md](./capabilities-and-setup.md), [resources-and-barriers.md](./resources-and-barriers.md), [synchronization.md](./synchronization.md), [commands-and-swapchain.md](./commands-and-swapchain.md)
