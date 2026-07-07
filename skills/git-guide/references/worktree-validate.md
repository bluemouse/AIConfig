# worktree-validate: Pre-Merge Validation Checkpoint

## Guideline

Validate a feature worktree before merge by running the project's typecheck, lint, build,
and test commands to ensure stability.

## Rationale

Running validation before merge catches issues early, ensures quality standards are met,
and verifies the feature aligns with plan criteria when configured.

## Example

```bash
# In feature worktree
cd ../services-feature-auth-flow

# Run validation checks — use the project's own commands
<project typecheck command>    # e.g. npm run typecheck, cmake --build, ./gradlew compileKotlin
<project lint command>         # e.g. npm run lint, ruff check, ./gradlew detekt
<project build command>        # e.g. npm run build, cmake --build build
<project test command>         # e.g. npm run test, ctest, ./gradlew test

# Check plan criteria if configured
git config branch.services/feature/auth-flow.plan
# "Implement email+password flow with TOTP and backup codes"

# Verify plan success criteria met:
# ✓ Email validation (part of LoginFlow)
# ✓ TOTP verification (part of LoginFlow)
# ✓ Backup codes support (in VerificationFlow)

# Overall status: READY TO MERGE
# All validation passed, all plan criteria met
```

## Techniques

- Verify in feature worktree
- Check commits complete
- Discover validation commands from project config (`package.json`, `Makefile`,
  `CMakeLists.txt`, `build.gradle.kts`, `pyproject.toml`, or repo docs) — do not assume
  `npm`
- Run validation in sequence: typecheck → lint → build → test (skip steps the project
  does not define)
- Check plan criteria if associated
- Report results
