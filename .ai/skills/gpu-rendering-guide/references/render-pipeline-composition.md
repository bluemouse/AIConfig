# render-pipeline-composition: Modular Render Pipeline and Extension Points

## Guideline

Split the render pipeline into a stable core graph plus pluggable extension passes registered at setup time; separate pass setup (resource declaration, graph wiring) from pass execution (command recording); and let features toggle on/off by registering or omitting extension passes without rewriting the core graph.

## Rationale

A monolithic render function that hard-codes every feature (SSR, SSAO, motion blur, debug overlays) becomes unmaintainable — every new effect requires editing the core loop and risks breaking existing passes. Production engines solve this with composable pipelines: Unreal's RDG pass registration and render plugins, Unity's Scriptable Render Pipeline with RendererFeatures, and Frostbite's nested frame-graph modules all share the same shape — a core graph declares stable resources and anchor passes; extensions declare their reads/writes and plug into named injection points; the graph compiler merges them, culls unused branches, and derives barriers. Toggling a feature means not registering its extension pass, not `#ifdef`-ing the core.

## How to Apply

1. **Define injection points** — Named slots in the core graph where extensions attach (e.g. `BeforeLighting`, `AfterPostProcess`, `Overlay`).
2. **Setup vs execute** — Setup registers passes and resource dependencies into the graph; execute records commands when the graph invokes the pass callback. Extensions implement the same interface.
3. **Extension registration** — At pipeline init, each enabled feature registers its passes and declares which injection point they attach to; disabled features register nothing and are culled by the graph.
4. **Resource contracts** — Extensions read/write only resources declared in the graph or created as transient within their own sub-graph; they cannot reach into undocumented core targets.
5. **Ordering within an injection point** — Assign explicit priority or dependency edges among extensions at the same slot so order is deterministic.
6. **Nested sub-graphs** — A complex extension (e.g. a full SSR chain) can be its own mini-graph compiled as a module and inserted as one logical pass.

## Example

```c
// Core graph + extension registration. Disabled features never enter the compiled graph.
typedef struct {
    const char *name;
    bool enabled;
    injection_point point;
    void (*setup)(render_graph *g, injection_point point);
    void (*execute)(render_graph *g, cmd_stream cmd);
    int priority;
} render_extension;

void build_frame_graph(render_graph *g, render_extension *exts[], int n_ext) {
    // Core passes — always present
    rg_add_pass(g, "gbuffer",  core_gbuffer_setup,  core_gbuffer_execute);
    rg_add_pass(g, "lighting", core_lighting_setup, core_lighting_execute);

    // Extensions plug into named injection points
    for (int i = 0; i < n_ext; ++i) {
        if (!exts[i].enabled) continue;
        exts[i].setup(g, exts[i].point);   // declares reads/writes, attaches to injection point
    }

    rg_compile(g);   // culls unreachable passes (disabled extensions vanish), plans barriers
}
```

## Gotchas

- An extension that reads a core resource the core pass did not export gets no barrier — extensions must declare every read/write, same rule as core passes, see [references/render-graph.md](./render-graph.md).
- Injection-point priority alone is not enough when extensions depend on each other — add explicit dependency edges between extensions at the same slot.
- Setup code that allocates resources outside the graph bypasses lifetime tracking and aliasing — all targets must be graph-managed or marked external.
- Hot-reloading an extension mid-frame requires rebuilding the graph at a safe boundary, same constraint as shader hot-reload.
- Too many small extension passes fragment the graph and increase barrier count — batch related work into one extension sub-graph when they share lifetimes.

## Related

[references/render-graph.md](./render-graph.md), [references/shader-system.md](./shader-system.md), [references/scene-rendering-culling.md](./scene-rendering-culling.md)
