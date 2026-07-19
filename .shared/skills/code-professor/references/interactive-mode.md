# Interactive mode

Trigger when the user says "guided study", "teach me interactively", "walk me through learning this codebase", or equivalent — or when the request is broad and choosing deliverable and depth would materially improve the first response.

## Setup prompt

Ask in one message before investigation work:

```
Let's set up this study:
1. Deliverable? (repository orientation / module deep dive / workflow trace / failure investigation)
2. Depth? (overview / standard / deep — default: standard)
3. Topic or scope? (whole repo, named module, named workflow, or symptom)
4. Audience? (e.g. new contributor, maintainer, coding agent — and assumed familiarity)
```

If the user already named deliverable, depth, or scope clearly, confirm rather than re-ask everything.

## Defaults when the user skips choices

- Broad "teach me this repo" → repository orientation, standard depth
- Named module → module deep dive, standard depth
- Named flow → workflow trace, standard depth
- Named failure → failure investigation, deep depth
