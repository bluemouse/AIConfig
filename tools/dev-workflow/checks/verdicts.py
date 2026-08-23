"""Single source of truth for checker verdict vocabularies.

This module defines the valid verdicts per checker artifact. The loop-contracts
reference (references/loop-contracts.md) documents these; this module is the
machine-readable source that loop_checks.py imports.

To change a verdict vocabulary, update this module AND the corresponding
section in references/loop-contracts.md.
"""

from __future__ import annotations

# Valid verdicts per checker artifact filename.
# Each set contains the exact verdict strings the checker must emit.
# The verdict is the first non-empty line after a "## Verdict" or
# "## Loop verdict" heading, with markdown emphasis (**bold**) stripped.
CHECKER_VERDICTS: dict[str, set[str]] = {
    "11-research-review.md": {
        "ready",
        "conditionally ready",
        "needs revision",
        "blocked",
    },
    "21-plan-review.md": {
        "validated",
        "conditionally validated",
        "needs revision",
        "blocked",
    },
    "31-implementation-audit.md": {
        "pass",
        "pass with risks",
        "fail",
        "blocked",
    },
    "40-code-review.md": {
        "ready to commit",
        "ready with notes",
        "needs revision",
    },
}

# Accept verdicts (loop exits forward) per checker artifact.
ACCEPT_VERDICTS: dict[str, set[str]] = {
    "11-research-review.md": {"ready", "conditionally ready"},
    "21-plan-review.md": {"validated", "conditionally validated"},
    "31-implementation-audit.md": {"pass", "pass with risks"},
    "40-code-review.md": {"ready to commit", "ready with notes"},
}

# Revise verdicts (loop continues) per checker artifact.
REVISE_VERDICTS: dict[str, set[str]] = {
    "11-research-review.md": {"needs revision"},
    "21-plan-review.md": {"needs revision"},
    "31-implementation-audit.md": {"fail"},
    "40-code-review.md": {"needs revision"},
}

# Blocked verdicts (escalate immediately) per checker artifact.
BLOCKED_VERDICTS: dict[str, set[str]] = {
    "11-research-review.md": {"blocked"},
    "21-plan-review.md": {"blocked"},
    "31-implementation-audit.md": {"blocked"},
    "40-code-review.md": set(),  # code-review has no blocked verdict
}


def strip_markdown_emphasis(text: str) -> str:
    """Strip markdown emphasis (**bold**, *italic*) from text."""
    return text.replace("**", "").replace("*", "").strip().lower()


def extract_verdict(text: str) -> str | None:
    """Extract the verdict from a checker report.

    Looks for a verdict after a "## Verdict" or "## Loop verdict" heading.
    Strips markdown emphasis and returns the lowercased verdict string.
    Returns None if no verdict heading is found.
    """
    import re

    # Look for verdict headings.
    patterns = [
        r"## Verdict\s*\n+([^\n]+)",
        r"## Loop verdict\s*\n+([^\n]+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            raw_verdict = match.group(1).strip()
            return strip_markdown_emphasis(raw_verdict)

    return None


def match_verdict(found_verdict: str, valid_verdicts: set[str]) -> bool:
    """Check if a found verdict matches any valid verdict exactly.

    Replaces the old substring matching, which was fragile (e.g., "ready"
    would match "ready to commit"). Now the found verdict must equal a
    valid verdict exactly, after stripping markdown emphasis.

    Exception: if the found verdict starts with a valid verdict followed by
    additional context (e.g., "ready — research is complete"), it matches.
    This allows checkers to add context after the verdict word.
    """
    for valid in valid_verdicts:
        if found_verdict == valid:
            return True
        # Allow "verdict — context" or "verdict - context" or "verdict: context"
        if found_verdict.startswith(valid):
            remainder = found_verdict[len(valid):].strip()
            if not remainder:
                return True
            # Must be followed by a separator (—, -, :, or end)
            if remainder[0] in ("—", "-", ":", "–"):
                return True
    return False
