"""EU AI Act checklist (2024/1689 as amended by 2026/1744)."""

from __future__ import annotations

import logging

from eu_ai_act_checklist.checklist import (
    DEFAULT_TABLE,
    Answers,
    Assessment,
    ChecklistError,
    Obligation,
    ObligationRow,
    assess,
    load_answers,
    render,
)

__all__ = [
    "DEFAULT_TABLE",
    "Answers",
    "Assessment",
    "ChecklistError",
    "Obligation",
    "ObligationRow",
    "__version__",
    "assess",
    "load_answers",
    "render",
]

__version__ = "0.1.0"

# Configure package logger with NullHandler as per library engineering standards
logging.getLogger(__name__).addHandler(logging.NullHandler())
