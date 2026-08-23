# Questioning Playbook

Use these prompts selectively. Ask one high-leverage question or present one decision at a time.

## Scope and decomposition
- Is this one feature, or does it contain separable products, services, or workflows?
- Which slice would deliver value first without requiring the whole vision?
- What is explicitly out of scope for the first implementation plan?
- What existing behavior must not change?

## Problem validation
- What user pain or business risk does this solve?
- What happens if this is not built?
- What current workaround proves demand?
- What must be true for this to be worth building?

## User and stakeholder clarity
- Who is the primary user: expert, casual, admin, developer, operator, or customer?
- Who benefits, who maintains it, and who can block it?
- What user action should become faster, safer, cheaper, or more reliable?
- What support or operational team inherits the failure cases?

## Requirements hardening
- Which requirement is a must-have versus a preference?
- What is the smallest acceptance test that proves this works?
- What data must be stored, transformed, displayed, audited, or deleted?
- What latency, quality, uptime, compatibility, or accessibility target matters?

## Alternatives and trade-offs
- What is the conservative approach?
- What is the ambitious approach?
- What is the reversible experiment?
- Which constraint dominates: speed, quality, cost, reliability, security, usability, or maintainability?

## Aggressive challenge prompts
Use these when the posture is aggressive or the idea is under-specified.

- This assumes [assumption]. What evidence supports it?
- This sounds like a solution before a problem. What problem are we optimizing for?
- The scope mixes [area a] and [area b]. Which one should be researched first?
- The success metric is not measurable. What observable outcome would prove success?
- The proposal creates a maintenance burden. Who owns it after launch?
- The happy path is clear, but what should happen when [failure mode] occurs?
- This may be overbuilt. What would be removed for a first version?
- This may be underbuilt. What would make the first version unsafe or unusable?

## Convergence prompts
- Based on the trade-offs, can we agree that [direction] is the default unless [condition] is disproven?
- Is [open question] blocking implementation planning, or can it become a planning risk?
- Should the report finalize now, or should the next iteration focus on [specific unknown]?
