"""Validation check modules for the dev-workflow harness.

Each module exposes check functions that return a list of Finding instances.
Entry-point scripts (validate_phase.py, validate_backward_edge.py,
check_pre_phase.py, check_post_phase.py) import and dispatch to these modules.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Finding:
    """A single validation finding."""

    severity: str  # "error" or "warning"
    check: str  # check category name
    message: str  # human-readable description

    def __str__(self) -> str:
        return f"[{self.severity}] {self.check}: {self.message}"
