# Source Synthesis

This skill is an original synthesis informed by three open-source skills requested by the user.

## 1. PM AI Partner - devil-advocate

Source: https://github.com/jeremylongshore/claude-code-plugins-plus-skills/tree/main/plugins/productivity/pm-ai-partner/skills/devil-advocate

Integrated ideas:

- constructive criticism intended to strengthen rather than discourage;
- challenge assumptions, edge cases, objections, and risks;
- acknowledge strengths;
- prioritize the largest issues;
- require actionable mitigations;
- tailor objections to stakeholders and proposal context.

## 2. LifeOS - RedTeam

Source: https://github.com/danielmiessler/LifeOS/tree/main/LifeOS/install/skills/RedTeam

Integrated ideas:

- decompose proposals into atomic claims;
- apply independent adversarial perspectives;
- distinguish attacks on ideas from attacks on systems;
- rank findings by severity and discard noise;
- combine steelmanning with a strong counter-case;
- compare competing proposals and synthesize a superior path;
- search for the single structural issue that can collapse the plan.

The packaged skill does not require a fixed number of agents. It uses independent lenses and explicitly avoids claiming parallel review when unavailable.

## 3. The Fool

Source: https://github.com/Jeffallan/claude-skills/tree/main/skills/the-fool

Integrated ideas:

- steelman before challenge;
- Socratic assumption analysis;
- dialectical counterargument and synthesis;
- pre-mortem and second-order failure reasoning;
- adversarial stakeholder analysis;
- falsification criteria and evidence grading;
- maintain intellectual honesty and concede points that survive.

## Added Synthesis and Extensions

This skill adds a unified decision and remediation layer:

- mandatory causal reasoning chain for every finding;
- explicit severity, confidence, evidence, and fixability dimensions;
- mandatory resolution engineering for every retained finding;
- strict `S4 - Show-stopper / Not fixable` gate;
- distinction between difficult, unproven, not fixed yet, and truly not fixable;
- integrated verdicts: proceed, proceed with conditions, rework, replace, or reject;
- decision gates, kill criteria, residual risk, and revised proposal output;
- automatic lens selection and one-pass synthesis rather than requiring a separate mode-selection exchange.

All three referenced repositories describe their material as MIT licensed at the repository level as of the synthesis date. Consult each repository for current license text and attribution requirements before redistributing copied source material. This package paraphrases and synthesizes concepts rather than bundling the original files.
