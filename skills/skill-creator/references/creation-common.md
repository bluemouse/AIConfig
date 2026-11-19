# Creation common — shared authoring skeleton

The ~50% of the creation process shared by **skill-creator**, **agent-creator**, and
**command-creator**. Each creator's SKILL.md holds only its per-kind delta; this file is
the shared backbone. Cross-links between the three resolve after install because all
installed skills sit at the same depth (`.agents/skills/<name>/`).

## Authoring path — bootstrap vs direct

Pick **one** path before writing files.

- **Bootstrap** (preferred for repo-maintained content revised and reinstalled over time):
  author under the repo's source-of-truth directory, validate, install with the
  installer script. The install output is generated — regenerated after every bootstrap
  edit.
- **Direct** (one-offs and quick first drafts): scaffold straight into the installed
  layout with the create script. The installed file is canonical; edit it directly.
- Do **not** hand-create installed directories or files — use the scripts.

## Authoritative-edit rule (applies everywhere in each creator)

1. **Never hand-edit installed output when bootstrap source exists.** Edit the bootstrap
   source, then reinstall — otherwise edits are lost on the next install.
2. Only on the direct path (no bootstrap source) is the installed file canonical.
3. **Validate after every substantive edit** — against the bootstrap path before install,
   and against the installed path after install or direct scaffold. Fix errors before
   handing off.

## Body shape

Tool-neutral body (role, workflows, output formats, success criteria, boundaries) with a
`## Tool notes` H2 at the end holding tool-native mechanics (spawn commands, reload steps,
frontmatter deltas) in per-tool `###` subsections — omitted entirely when there are none.
The validator flags tool-specific content in the neutral body. Frontmatter
`name`/`description` rules specific to each kind (trigger descriptions, length caps,
invocation gating) stay in each creator's SKILL.md — only the generic rule is shared
here: keep all "when to use" phrasing in the `description`, not the body.

## Capture intent

Extract tools, steps, corrections, and formats from conversation history first; use
user-supplied wording **verbatim** in generated files; confirm gaps with the user. Match
the target repo's existing conventions. When ambiguity exceeds intake — skill vs agent
vs command, conflicting requirements, no shared picture of success — run the
clarification loop in [../../prompt-clarifier/SKILL.md](../../prompt-clarifier/SKILL.md)
and carry its requirement ledger into the body and `description`.

## Description tuning (manual, all tools, all kinds)

The `description` drives discovery/triggering; the `name` + `description` are matched
against the user's request. After creating or improving content, offer to tune it:

1. Draft ~10–20 realistic should-trigger / should-not-trigger queries, concrete and
   edge-case heavy.
2. Review them with the user; mark false positives and false negatives.
3. Revise the description: for skills this can be the automated eval loop
   (skill-creator's `run_loop.py`, per its `## Tool notes`); agents and commands
   revise manually.
4. Apply the revised `description` at the authoritative edit location; reinstall
   or re-sync the installed copy. Show before/after when possible.

Automated description-eval loops exist **only for skills** (skill-creator's
`run_loop.py`, per its `## Tool notes`) — agents and commands tune manually on every
tool.

## Output summary (all kinds)

After creating or installing files, summarize: the authoritative edit path, the
installed path(s), and any assumptions made about instructions or triggers.

## Test-and-iterate loop

1. Draft 2–3 realistic test prompts with the user; note expected behavior and the
   efficiency signal to watch for.
2. Run them on the target tool (spawn mechanics per the kind's `## Tool notes`).
3. Review runs for correctness (scope, accuracy, hallucinated files or APIs),
   completeness (edge cases, output format), and efficiency — read transcripts, not just
   final outputs.
4. Edit at the authoritative edit location; reinstall if bootstrap; re-validate and
   re-test. Repeat until the user is satisfied or progress stalls.
5. Improvement rules: **generalize** (fixes must help beyond the test examples), **keep
   the file lean**, **edit the tool-neutral body first** (then Tool notes for tool-only
   gaps), **explain why** (reasoning over ALL-CAPS MUSTs), **bundle repeated work** under
   `scripts/`. Do not stop partway through a planned test iteration.
6. Decline misleading, covert, or unauthorized-access requests.
