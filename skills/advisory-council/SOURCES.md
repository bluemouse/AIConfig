# Provenance and Design Notes

This skill is an original synthesis informed by four public skill designs:

- LifeOS `Council`: multi-agent debate with a small, diverse council and parallel hypothesis testing.
- typia `discussion`: iterative participant discussion and convergence around a shared technical problem.
- Claude Code Templates `think-tank`: moderated, role-diverse debate with user context, trade-offs, and conditional recommendations.
- oh-my-openagent `hyperplan`: independent analysis, cross-critique, defense or concession, and filtering to insights that survive adversarial review.

The implementation generalizes those ideas into a tool-agnostic protocol with:

- dynamic role selection rather than fixed personalities or model categories;
- evidence and claim ledgers;
- explicit belief updating and minority reports;
- ranked options with sensitivity analysis;
- convergence and stop rules;
- native-agent, delegated-agent, and honest simulated fallbacks;
- final decision or plan delivery rather than debate-only output.

Source locations consulted:

- https://github.com/danielmiessler/LifeOS/tree/main/LifeOS/install/skills/Council
- https://github.com/samchon/typia/tree/master/.agents/skills/discussion
- https://github.com/davila7/claude-code-templates/tree/main/cli-tool/components/skills/productivity/think-tank
- https://github.com/code-yeongyu/oh-my-openagent/tree/dev/.agents/skills/hyperplan
