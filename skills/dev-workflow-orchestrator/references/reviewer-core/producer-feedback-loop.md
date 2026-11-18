# Producer Feedback Loop (shared by plan-guide and research-guide)

Use this protocol when the user provides a reviewer report, review findings, or a handoff
packet. Per-skill parameters:

| parameter | plan-guide | research-guide |
|---|---|---|
| Reviewer | plan-reviewer | research-reviewer |
| Artifact | implementation plan | research report |
| Accept verdict | `validated` | `ready` |
| Conditional verdict | `conditionally validated` | `conditionally ready` |
| Downstream step | execution (plan-executor) | implementation planning (plan-guide) |
| Handoff contract | plan-reviewer's `guide-handoff-contract.md` | research-reviewer's `research-guide-handoff-contract.md` |
| Finding-id prefix | `pr-*` | `rr-*` |
| Stable ids to preserve | task ids, test ids, verification ids | requirement ids, evidence ledger items, risk ids, open-question ids |

## 1. Parse reviewer output

Extract from the review report and handoff packet: verdict (accept / conditional / needs revision / blocked), confidence, downstream recommendation, iteration required, highest-priority repair track, recommended repair mode, sections or ids to preserve unchanged, findings (ids, severity, affected sections, issue, required fix, and producing-skill action), user decisions needed, upstream issues or evidence gaps, findings accepted as risks, rejected findings, re-review requirement, and active reviewer roles/domain assumptions.

If the review lacks a handoff packet, synthesize one from verdict, findings, and required fixes using the handoff contract's field list. Treat `proceed with accepted risks` as explicitly accepted risks recorded in the artifact — not informal conditions.

## 2. Decide whether another iteration is required

| reviewer verdict | producing-skill response |
|---|---|
| Accept | No repair iteration required. Offer finalization, optional polish, or downstream handoff. |
| Conditional | Ask whether to accept remaining risks or repair them before the downstream step. |
| Needs revision | Require at least one targeted repair iteration before claiming readiness. |
| Blocked | Do not claim readiness. Resolve blocker findings or produce a blocked artifact. |

Severity override: any unresolved blocker prevents readiness; any unresolved major finding prevents the accept verdict unless explicitly accepted as a risk under the conditional verdict; minor/nit findings can be fixed opportunistically or carried if visible.

Honor `Iteration required` and the packet's re-review requirement. After a blocked verdict, require re-review before the downstream step. After needs revision, re-review unless every finding was trivial and self-evidently fixed.

## 3. Choose repair mode and preserve stable structure

Use the packet's recommended repair mode and preserve-unchanged list to minimize churn. Repair modes (use the ones the reviewer named): **blocker-only repair** (only blockers remain, rest is sound), **targeted section repair** (default when findings map to specific sections or ids), **full rewrite** (broadly unsafe, internally inconsistent, or untraceable), **narrow scope** (independent subsystems/products mixed), **split plan** (plan-guide: independent subsystems become separate plans), **research iteration** (research-guide: new evidence, user decisions, codebase inspection, or domain clarification needed), or **none**.

- Preserve listed stable ids and validated sections unless a finding requires changing them.
- Keep original finding ids for unresolved or partially resolved issues; create new ids only for genuinely new issues.
- Mark findings resolved, partially resolved, reopened, accepted as risk, rejected with rationale, or still blocking per the shared re-review protocol.

## 4. Triage each finding

Classify each material finding: **revise artifact** (existing context suffices), **ask user** (a scope/product/risk/priority/decision input is required), **inspect codebase** (repository facts must be checked), **research upstream** (plan-guide: source research/spec insufficient), **gather evidence** (research-guide: external/internal/domain facts must be sourced), **validate assumption** (research-guide: an important claim must be confirmed, disproven, or downgraded), **resolve open question** (research-guide: a blocking question answered or carried as risk), **reconcile contradiction** (research-guide: sections disagree), **expand alternatives** (research-guide: credible options were omitted), **narrow scope**, **split plan** (plan-guide), **accept as risk** (non-blocker, explicit only), **reject with rationale** (out of scope, contradicted, or reviewer misunderstanding), or **still blocking**.

Do not silently reject or drop prior blocker or major findings.

## 5. Produce a repair summary before editing

```markdown
<Reviewer> triage:
- Verdict received: [verdict, confidence]
- Downstream recommendation: [proceed | proceed with accepted risks | revise first | do not proceed]
- Repair iteration required: yes/no
- Repair mode: [modes from §3]
- Sections or ids to preserve unchanged: [list]
- Highest-impact issue: [finding id and summary]
- Proposed repair track: [one of the §4 classes]
- Findings to resolve now: [ids]
- Findings to carry, reject, or leave blocked: [ids and rationale]
- Re-review required before the downstream step: [yes | no | recommended]
```

Then either revise the artifact or ask the one next required question.

## 6. Update the artifact

When finalizing after reviewer feedback, include a **Reviewer feedback status** section with: latest reviewer verdict and confidence; findings resolved, partially resolved, and reopened (original ids preserved); findings accepted as risks; findings rejected with rationale; remaining blockers or major issues; and whether another reviewer pass is needed. Prefer a clearly blocked artifact over a misleading ready one.
