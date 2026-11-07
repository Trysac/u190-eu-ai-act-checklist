"""Behavior tests for the public API of eu_ai_act_checklist."""

from __future__ import annotations

import eu_ai_act_checklist


def test_version_is_semver() -> None:
    parts = eu_ai_act_checklist.__version__.split(".")
    assert len(parts) == 3
    assert all(part.isdigit() for part in parts)
