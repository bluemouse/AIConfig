# code-review-and-audit: Vulkan Review Checklist, Spec Audit, and Validation

Use this reference when reviewing a Vulkan renderer or compute code, auditing API validity, or diagnosing validation-layer errors. Report correctness issues before performance issues. Run [scripts/vulkan_antipattern_scan.py](../scripts/vulkan_antipattern_scan.py) on supplied source trees first for review prompts (it flags patterns, it does not prove code invalid).

## Authority order (for spec questions)

1. Vulkan Specification and reference pages — valid usage, object lifetime, synchronization, feature/extension requirements, exact semantics.
2. Vulkan Guide — practical interpretation, feature enabling, synchronization examples, memory allocation, common pitfalls.
3. Vulkan Samples — implementation patterns.
4. Vendor performance guides — hardware-specific optimization.
5. Existing engine/project conventions when they do not conflict with the spec.

Do not invent VUIDs, promotion status, mandatory limits, or signatures. For "is this valid usage?", "which VUID?", "is this extension core in 1.3?", consult the spec/reference before finalizing; if sources are unavailable, state what is uncertain and give a conservative correction.

## Audit process

1. Identify the API object/function/struct/feature in question.
2. Identify the selected API version and enabled extensions.
3. Classify it: core 1.3, promoted extension path, or optional extension.
4. Verify every required feature bit was queried and enabled at `VkDevice` creation.
5. Verify every extension used was enumerated and enabled at correct instance/device scope.
6. Verify pNext chains: correct `sType`, no duplicate incompatible structs, storage live until the call returns, no unsupported fields set true.
7. Verify object lifetime and host-synchronization rules.
8. Verify queue-family ownership and queue capability.
9. Verify command-buffer recording state and render-pass/dynamic-rendering scope.
10. Verify memory availability/visibility barriers and image layouts.
11. Verify descriptor set/layout/pipeline-layout compatibility.
12. Verify format features and limits.

## Finding classification

- **Invalid / spec violation**: violates a valid-usage rule or uses unsupported/disabled functionality.
- **Undefined or unsafe**: functionality used without required enablement, lifetime proof, or synchronization.
- **Likely performance issue**: legal but causes stalls, bandwidth waste, CPU overhead, or driver work.
- **Portability risk**: legal on one implementation but relies on optional limits/features/formats.
- **Style/maintainability issue**: legal but fragile or hard to audit.

## Correctness-first checklist

- [ ] API version chosen deliberately; no accidental newer-than-target APIs.
- [ ] Instance/device extensions and layers enumerated before enabling.
- [ ] Features queried with `vkGetPhysicalDeviceFeatures2` and enabled via a valid pNext chain; no unsupported bits enabled.
- [ ] Required queues exist and present support checked for the surface.
- [ ] Required formats, sample counts, image usages, and present modes checked.
- [ ] All `VkResult` failures that can occur are handled; `sType`/pNext correct.
- [ ] Object lifetimes cover GPU in-flight use; host-synchronization rules obeyed for externally synchronized objects.

### Synchronization and lifetime

- [ ] Uses synchronization2 on the 1.3 path; barriers match producer/consumer stages and access masks.
- [ ] Image layouts match actual usage and transitions are tracked.
- [ ] Queue-family ownership transfers present when resources cross families (release/acquire paired).
- [ ] Frame resources retired by fences/timeline values, not idle waits; swapchain/per-frame resources not reused before safe.
- [ ] Host flush/invalidate correct for non-coherent memory.

### Memory and resources

- [ ] Routine resources sub-allocated, not individually allocated; dedicated allocations only where appropriate.
- [ ] Memory type selection respects device-local/host-visible/coherent/cached/lazily-allocated needs; alignment handled.
- [ ] Upload/readback paths explicit; budget and large-resource behavior considered.

### Descriptors and pipeline layout

- [ ] Descriptor layouts match shader declarations; pipeline layouts compatible with bound sets and push constants.
- [ ] No descriptor updates while in-flight GPU work may read them (unless safely managed update-after-bind).
- [ ] No per-draw descriptor allocation/update unless intentionally measured.
- [ ] Descriptor-indexing features enabled before bindless/runtime-array/partially-bound/update-after-bind usage.

### Pipelines and rendering

- [ ] Pipeline creation not unexpectedly in the render loop; cache/warmup strategy exists.
- [ ] Dynamic-rendering pipeline info matches runtime attachment formats/sample counts; load/store ops intentional.
- [ ] Depth/stencil state and layouts correct; shader modules/reflection validated.

### Command buffers and queues

- [ ] Command pools per thread or externally synchronized; usage flags match usage.
- [ ] Secondary buffers chunky enough; submissions batched sensibly.
- [ ] Async compute/transfer justified by profiling or clear workload overlap.

### Compute-specific

- [ ] Queue supports compute; workgroup sizes within limits; dispatch handles non-divisible counts.
- [ ] Storage image/buffer features checked; barriers between dispatches/transfers/graphics/host reads.
- [ ] Subgroup assumptions queried, with fallback where needed.

## Common audit red flags

- Feature struct queried but not in the device-create enable chain.
- Extension enumerated but not enabled, or enabled at wrong scope; extension feature used without its feature bit.
- Core/extension function names mixed without a compatibility abstraction.
- pNext object out of lifetime before the create/query call.
- Legacy barrier API in a 1.3 codebase without reason; access masks incompatible with stage masks.
- `TOP_OF_PIPE`/`BOTTOM_OF_PIPE`/`ALL_COMMANDS` as catch-all synchronization.
- Missing acquire/release queue-family ownership transfer.
- Host writes to non-coherent memory without flush; reads without invalidate.
- Destroying resources before in-flight GPU work completes; descriptor updates the GPU can still read.
- Pipeline layout incompatible with shader resources; format sampled linear-filtered or used as storage without querying format features.

## Validation-layer workflow

Recommend separate modes: core validation (routine dev), synchronization validation (barrier/layout/lifetime hazards), GPU-assisted validation (shader-side descriptor/indexing/out-of-bounds), best-practices validation (performance/portability). Validation does not guarantee correctness — some performance, external-sync, timing, and driver-specific issues still require review and profiling.

## Review output templates

Design/implementation response:

```markdown
## Assumptions and target
Vulkan version, platform class, graphics vs compute, performance priority.
## Capability gates
Required version, features, extensions, and fallback behavior.
## Implementation
Valid pNext chains, synchronization, resource lifetime, error handling.
## Validation
What validation/tools should catch, plus likely blind spots.
## Performance notes
What to measure and what not to assume.
```

Code-review response:

```markdown
## Blocking correctness issues
Invalid API usage, lifetime, synchronization, feature/extension misuse, missing error paths.
## High-risk performance issues
Unnecessary stalls, bad memory allocation, descriptor churn, pipeline hitches, bad barriers.
## Vulkan 1.3 modernization
Core replacements or simplifications.
## Suggested patch
```cpp
// corrected snippet
```
## Validation/profiling to run
Exact validation mode/tool signal.
```

Synchronization hazard diagnostic:

```text
hazard: [resource] written as [usage/layout] in [pass a], read as [usage/layout] in [pass b]
missing/weak dependency: [src stage/access] -> [dst stage/access]
recommended barrier: [specific sync2 fields]
why: [correctness issue or performance bubble]
```

## Related

[best-practices.md](./best-practices.md), [capabilities-and-setup.md](./capabilities-and-setup.md), [resources-and-barriers.md](./resources-and-barriers.md), [synchronization.md](./synchronization.md)
