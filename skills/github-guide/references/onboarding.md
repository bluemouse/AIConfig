# First-time GitHub CLI setup

Get from a bare machine to a working `gh`: install, authenticate, pick a git protocol, clone, and verify with a read call. Token families and per-operation scopes are in [auth.md](auth.md).

## Rules the first-run flow must respect

- **Never run `gh auth login` inside the agent** — it opens an interactive browser/device
  flow that blocks the terminal. Stop and ask the user to authenticate themselves, then
  resume.
- **Do not feed a fine-grained PAT to `gh auth login --with-token`** — its per-resource
  scoping confuses that flow. Export fine-grained PATs as `GH_TOKEN`
  (`GH_ENTERPRISE_TOKEN` for GHES) instead; `--with-token` is for classic PATs only.
- HTTPS git operations won't use `gh` credentials after a token/env login until
  `gh auth setup-git` makes `gh` the git credential helper.
- `gh auth status` exits non-zero on auth problems, but with `--json` it exits 0 even when
  broken — back it with a real read call (`gh api user -q '.login'`).
- GHES: `gh auth login --hostname ghe.example.com`, then `GH_HOST=ghe.example.com` and
  `GH_ENTERPRISE_TOKEN` (never `GH_TOKEN` — mixing them is the classic
  "works on github.com, 401 on GHES").
