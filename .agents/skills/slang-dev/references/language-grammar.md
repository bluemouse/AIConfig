# Slang Language Grammar and Shader Syntax Reference

Compact grammar-oriented checklist for Slang shader authoring. Not a replacement for the [normative spec](https://github.com/shader-slang/spec) or compiler diagnostics; verify uncertain constructs with `slangc`.

## Source and Module Structure

Typical source-unit forms:

```ebnf
source-unit      := module-decl? declaration*
module-decl      := 'module' qualified-name ';'
declaration      := import-decl | visibility? top-level-decl | extension-decl
import-decl      := 'import' qualified-name ';'
                 | '__exported' 'import' qualified-name ';'   /* experimental re-export */
qualified-name   := identifier ('.' identifier)*
visibility       := 'public' | 'internal' | 'private'
```

Guidance:
- One logical module per primary `.slang` file when possible: `module Renderer.Lighting;`.
- `import` loads a separate module; it does not paste text or share preprocessor state.
- Use `__exported import` only when this module intentionally re-exports another module's API (experimental).
- Use `public` deliberately for declarations consumed from other modules or C++ entry-point discovery.

### Multi-file modules (`__include`)

Additional files join a module via `__include` (not `#include`):

```slang
// scene.slang
module scene;
__include "scene-helpers";

// scene-helpers.slang
implementing scene;
// ... declarations visible throughout module scene
```

`__include` semantics:
- Preprocessor state does not propagate across `__include` boundaries (unlike `#include`).
- Each file is included exactly once; circular `__include` is allowed.
- All files in a module share `internal` visibility scope; only the primary file starts with `module`.

Only the primary module file may be `import`ed — never `import` an `implementing` helper file directly.

### Legacy modules (deprecated)

A module is legacy when it lacks a `module` declaration, uses no `__include`, and uses no visibility modifiers. All symbols are treated as `public`. Do not use this pattern in new code.

## Lexical and Type Forms

Common scalar/vector/matrix forms:

```slang
bool b;
int i; uint u; float f; half h; double d; // target support varies
float2 uv; float3 n; float4 color;
float4x4 worldToClip;
```

Generic type forms:

```ebnf
type             := builtin-type | user-type | vector-type | matrix-type | resource-type | generic-app
vector-type      := scalar-type integer-literal          // float3, uint4
matrix-type      := scalar-type integer-literal 'x' integer-literal // float4x4
generic-app      := identifier '<' type-or-value-list '>'
```

Shader resource examples:

```slang
Texture2D<float4> gTex;
SamplerState gSampler;
StructuredBuffer<float4> gIn;
RWStructuredBuffer<float4> gOut;
ConstantBuffer<FrameParams> gFrame;
ParameterBlock<MaterialParams> gMaterial;
```

Layout-sensitive rule: use explicit types for host-visible data, public interfaces, matrices, and resource declarations; use `var` only for local values where the inferred type is obvious.

## Access Control

| Modifier | Scope |
|----------|-------|
| `public` | Visible across modules |
| `internal` | Visible within the module (default for new modules) |
| `private` | Visible within the enclosing type only |

Rules:
- A `public` signature must not expose less-visible types.
- Type definitions cannot be `private`.
- Interface requirements cannot be `private`.

## Expressions, Statements, and Local Bindings

```ebnf
block            := '{' statement* '}'
statement        := decl-stmt | expr-stmt | if-stmt | for-stmt | while-stmt | return-stmt | break-stmt | continue-stmt
local-binding    := ('let' | 'var' | type) identifier ('=' expression)? ';'
if-stmt          := 'if' '(' expression ')' statement ('else' statement)?
for-stmt         := 'for' '(' init? ';' condition? ';' next? ')' statement
return-stmt      := 'return' expression? ';'
```

Use `let` for immutable locals:

```slang
let ndotl = saturate(dot(n, l));
var accum = float3(0.0);
```

## Declarations and Entry Points

Function and entry-point pattern:

```ebnf
function-decl    := attributes? type identifier generic-params? '(' params? ')' constraints? block
param            := direction? type identifier semantic?
direction        := 'in' | 'out' | 'inout'
semantic         := ':' identifier
attribute        := '[' identifier ('(' args? ')')? ']'
```

Shader stage examples (use `fragment`, not `pixel`, in `[shader(...)]`):

```slang
struct VSIn  { float3 position : POSITION; float2 uv : TEXCOORD0; };
struct VSOut { float4 position : SV_POSITION; float2 uv : TEXCOORD0; };

[shader("vertex")]
VSOut vertexMain(VSIn input) { /* ... */ }

[shader("fragment")]
float4 fragmentMain(VSOut input) : SV_Target { /* ... */ }

[shader("compute")]
[numthreads(8, 8, 1)]
void computeMain(uint3 tid : SV_DispatchThreadID) { /* ... */ }
```

Prefer `[shader(...)]` on entry points even when the build also passes `-entry` and `-stage`. Required for `IModule::findEntryPointByName`.

## Structs, Classes, Interfaces, Generics

```slang
struct MaterialParams
{
    float4 baseColor;
    float metallic;
    float roughness;
};

interface BRDF
{
    float3 eval(float3 n, float3 v, float3 l);
}

struct Lambert : BRDF
{
    float3 albedo;
    float3 eval(float3 n, float3 v, float3 l) { return albedo * saturate(dot(n, l)); }
}

float3 shade<T : BRDF>(T brdf, float3 n, float3 v, float3 l)
{
    return brdf.eval(n, v, l);
}
```

Rules:
- Use interfaces/generics to replace macro specialization when variants are type-level or algorithmic.
- Keep generic constraints explicit (`T : Interface`).
- Avoid unconstrained generics in hot paths unless specialization count is bounded.
- Associated types and interface-typed values are advanced; use when dependent types or dispatch are required.

## Capabilities and Target-Sensitive Code

Capability atoms model targets, stages, API extensions, and hardware features. Requirements use `[require(...)]`:

```slang
[require(spvShaderClockKHR)]
[require(glsl, GL_EXT_shader_realtime_clock)]
[require(hlsl_nvapi)]
uint2 getClock() { /* ... */ }
```

Each `[require]` is a conjunction; multiple attributes form a disjunction. Target and stage atoms are mutually exclusive within their groups.

Rules:
- **Public and interface methods** must declare capability requirements explicitly — omitting `[require]` means no specific capability is required.
- **Internal/private** functions infer requirements from their bodies.
- **Entry points:** explicit `[require]` recommended; inferred if omitted, with errors when incompatible with the compile target.
- Prefer `[require(...)]` and target-specific modules over hidden backend behavior.
- Use `__target_switch` / `__stage_switch` for intentional backend/stage divergence instead of `#ifdef`.
- Do not assume a Vulkan SPIR-V feature exists on Metal; gate with capabilities and verify generated MSL.

## Parameter Blocks and Host Interface

`ParameterBlock<T>` groups parameters into an independent descriptor set (Vulkan) or argument buffer (Metal):

```slang
struct FrameParams { float4x4 viewProj; float3 cameraPos; };
struct MaterialParams { float4 baseColor; float roughness; };

ParameterBlock<FrameParams> gFrame;
ParameterBlock<MaterialParams> gMaterial;
Texture2D<float4> gBaseColor;
SamplerState gLinearSampler;
```

Layout rules (SPIR-V / Vulkan):
- Each non-nested `ParameterBlock` maps to one descriptor set with a dedicated set number.
- If `T` contains ordinary data (non-zero byte size), Slang auto-introduces a uniform buffer at **binding 0** of that set; resource fields bind at higher indices offset accordingly.
- Global-scope ordinary uniforms group into a default constant buffer.
- Entry-point `uniform` ordinary parameters become push constants in SPIR-V unless marked `[vk::push_constant]`.
- `ConstantBuffer`, `ParameterBlock`, structured buffers, and pointers use C/C++ struct layout rules on SPIR-V — not HLSL register packing.

Guidance:
- Group by update frequency: frame, view, pass, material, object, draw.
- Use reflection to map groups to Vulkan descriptor sets/bindings and Metal argument buffers/slots.
- Nested `ParameterBlock` fields create nested descriptor sets; keep nesting shallow for Metal compatibility.

## Stage Vocabulary

Slang stage strings for `[shader(...)]`:
- `vertex`
- `fragment` (pixel stage)
- `compute`

Advanced stages (mesh, ray tracing, etc.) only after checking target capability, generated code, and Metal maturity.

## Common Syntax Mistakes to Catch

- Missing `module` declaration in modular code.
- Using `#include` when `import` or `__include` was intended.
- Treating unqualified declarations as module-private — default is `internal`, not hidden from the rest of the module.
- Missing `[shader("compute")]` or `[numthreads(...)]` on compute entry points.
- Hard-coding bindings without checking reflection.
- Using pointers, descriptor handles, or SPIR-V-only features without capability gating and Metal fallback.
- Relying on default matrix layout or implicit host struct packing.
