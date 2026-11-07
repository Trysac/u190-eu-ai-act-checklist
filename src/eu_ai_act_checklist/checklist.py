"""Core implementation of the EU AI Act checklist library."""

from __future__ import annotations

import json
import logging
import re
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date
from typing import Literal

logger = logging.getLogger(__name__)

ErrorCode = Literal["input_too_large", "invalid_json", "unknown_question", "invalid_answer"]
Category = Literal["prohibited", "high_risk", "limited", "minimal"]
Role = Literal["provider", "deployer"]
AnnexIIIArea = Literal[
    "biometrics",
    "critical_infrastructure",
    "education",
    "employment",
    "essential_services",
    "law_enforcement",
    "migration",
    "justice_democracy",
]
Art5Point = Literal["a", "b", "c", "d", "e", "f", "g", "h", "ba", "bb"]

VALID_ART5_POINTS: frozenset[str] = frozenset({"a", "b", "c", "d", "e", "f", "g", "h", "ba", "bb"})
VALID_ANNEX_III_AREAS: frozenset[str] = frozenset(
    {
        "biometrics",
        "critical_infrastructure",
        "education",
        "employment",
        "essential_services",
        "law_enforcement",
        "migration",
        "justice_democracy",
    }
)
KNOWN_QUESTIONS: frozenset[str] = frozenset(
    {
        "role",
        "art5",
        "annex_i_safety_component",
        "annex_iii_area",
        "art6_3_exception",
        "profiling",
        "interacts_with_persons",
        "generates_synthetic_content",
        "emotion_or_biometric_categorisation",
        "deepfake",
        "gpai",
    }
)


class ChecklistError(Exception):
    """Base exception raised for checklist validation or loading errors."""

    def __init__(self, code: ErrorCode, message: str) -> None:
        super().__init__(message)
        self.code: ErrorCode = code


@dataclass(frozen=True)
class ObligationRow:
    """Entry in the obligations table."""

    article: str
    title: str
    applies_from: date
    applies_from_annex_i: date | None = None


@dataclass(frozen=True)
class Obligation:
    """Resulting triggered obligation."""

    id: str
    article: str
    title: str
    applies_from: date


@dataclass(frozen=True)
class Answers:
    """Validated user answers."""

    role: Role
    art5: tuple[Art5Point, ...] = ()
    annex_i_safety_component: bool = False
    annex_iii_area: AnnexIIIArea | None = None
    art6_3_exception: bool = False
    profiling: bool = False
    interacts_with_persons: bool = False
    generates_synthetic_content: bool = False
    emotion_or_biometric_categorisation: bool = False
    deepfake: bool = False
    gpai: bool = False


@dataclass(frozen=True)
class Assessment:
    """Assessment output."""

    category: Category
    obligations: tuple[Obligation, ...]
    notes: tuple[str, ...]


DEFAULT_TABLE: Mapping[str, ObligationRow] = {
    "art4": ObligationRow(
        article="Art. 4",
        title="AI literacy measures",
        applies_from=date(2025, 2, 2),
    ),
    "art5": ObligationRow(
        article="Art. 5",
        title="Do not place on the market or use (prohibited practice)",
        applies_from=date(2025, 2, 2),
    ),
    "art5_ba_bb": ObligationRow(
        article="Art. 5",
        title="Do not place on the market or use (prohibited practice)",
        applies_from=date(2026, 12, 2),
    ),
    "art6_4": ObligationRow(
        article="Art. 6(4)",
        title="Document the Art. 6(3) assessment before placing on the market",
        applies_from=date(2027, 12, 2),
    ),
    "art49_2": ObligationRow(
        article="Art. 49(2)",
        title="Registration of the Art. 6(3) exception",
        applies_from=date(2026, 8, 2),
    ),
    "art9": ObligationRow(
        article="Art. 9",
        title="Risk management system",
        applies_from=date(2027, 12, 2),
        applies_from_annex_i=date(2028, 8, 2),
    ),
    "art10": ObligationRow(
        article="Art. 10",
        title="Data and data governance",
        applies_from=date(2027, 12, 2),
        applies_from_annex_i=date(2028, 8, 2),
    ),
    "art11": ObligationRow(
        article="Art. 11",
        title="Technical documentation",
        applies_from=date(2027, 12, 2),
        applies_from_annex_i=date(2028, 8, 2),
    ),
    "art12": ObligationRow(
        article="Art. 12",
        title="Record-keeping (logs)",
        applies_from=date(2027, 12, 2),
        applies_from_annex_i=date(2028, 8, 2),
    ),
    "art13": ObligationRow(
        article="Art. 13",
        title="Transparency and instructions for deployers",
        applies_from=date(2027, 12, 2),
        applies_from_annex_i=date(2028, 8, 2),
    ),
    "art14": ObligationRow(
        article="Art. 14",
        title="Human oversight",
        applies_from=date(2027, 12, 2),
        applies_from_annex_i=date(2028, 8, 2),
    ),
    "art15": ObligationRow(
        article="Art. 15",
        title="Accuracy, robustness and cybersecurity",
        applies_from=date(2027, 12, 2),
        applies_from_annex_i=date(2028, 8, 2),
    ),
    "art17": ObligationRow(
        article="Art. 17",
        title="Quality management system",
        applies_from=date(2027, 12, 2),
        applies_from_annex_i=date(2028, 8, 2),
    ),
    "art26": ObligationRow(
        article="Art. 26",
        title="Deployer obligations",
        applies_from=date(2027, 12, 2),
        applies_from_annex_i=date(2028, 8, 2),
    ),
    "art27": ObligationRow(
        article="Art. 27",
        title="Fundamental rights impact assessment (check whether Art. 27(1) applies to you)",
        applies_from=date(2027, 12, 2),
        applies_from_annex_i=date(2028, 8, 2),
    ),
    "art43": ObligationRow(
        article="Art. 43",
        title="Conformity assessment",
        applies_from=date(2027, 12, 2),
        applies_from_annex_i=date(2028, 8, 2),
    ),
    "art49": ObligationRow(
        article="Art. 49",
        title="Registration in the EU database",
        applies_from=date(2027, 12, 2),
        applies_from_annex_i=date(2028, 8, 2),
    ),
    "art50_1": ObligationRow(
        article="Art. 50(1)",
        title="Inform people they interact with an AI system",
        applies_from=date(2026, 8, 2),
    ),
    "art50_2": ObligationRow(
        article="Art. 50(2)",
        title="Mark synthetic content as machine-readable",
        applies_from=date(2026, 8, 2),
    ),
    "art50_3": ObligationRow(
        article="Art. 50(3)",
        title="Inform people exposed to emotion recognition or biometric categorisation",
        applies_from=date(2026, 8, 2),
    ),
    "art50_4": ObligationRow(
        article="Art. 50(4)",
        title="Disclose deep fakes",
        applies_from=date(2026, 8, 2),
    ),
    "art53": ObligationRow(
        article="Art. 53",
        title="GPAI provider obligations",
        applies_from=date(2025, 8, 2),
    ),
    "art72": ObligationRow(
        article="Art. 72",
        title="Post-market monitoring",
        applies_from=date(2027, 12, 2),
        applies_from_annex_i=date(2028, 8, 2),
    ),
    "art73": ObligationRow(
        article="Art. 73",
        title="Serious incident reporting",
        applies_from=date(2027, 12, 2),
        applies_from_annex_i=date(2028, 8, 2),
    ),
}

DISCLAIMER = (
    "Technical aid, not legal advice. Based on Regulation (EU) 2024/1689 "
    "as amended by Regulation (EU) 2026/1744 (dates checked 2026-11-07); check later amendments."
)


def load_answers(text: str, *, max_bytes: int = 65_536) -> Answers:
    """Parse and validate answers from JSON text."""
    encoded = text.encode("utf-8")
    if len(encoded) > max_bytes:
        raise ChecklistError(
            "input_too_large",
            f"Input size ({len(encoded)} bytes) exceeds limit ({max_bytes} bytes)",
        )

    try:
        data = json.loads(text)
    except Exception as exc:
        raise ChecklistError("invalid_json", f"Invalid JSON payload: {exc}") from exc

    if not isinstance(data, dict):
        raise ChecklistError("invalid_json", "JSON payload must be an object")

    for key in data:
        if key not in KNOWN_QUESTIONS:
            sanitized = str(key)[:50]
            raise ChecklistError("unknown_question", f"Unknown question: '{sanitized}'")

    role = data.get("role")
    if role not in ("provider", "deployer"):
        raise ChecklistError(
            "invalid_answer",
            f"'role' must be 'provider' or 'deployer', got {role!r}",
        )

    art5_raw = data.get("art5", [])
    if not isinstance(art5_raw, list):
        raise ChecklistError("invalid_answer", "'art5' must be a list of strings")
    art5_list: list[Art5Point] = []
    for p in art5_raw:
        if not isinstance(p, str) or p not in VALID_ART5_POINTS:
            sanitized = str(p)[:50]
            raise ChecklistError("invalid_answer", f"Invalid Art. 5 point: '{sanitized}'")
        art5_list.append(p)  # type: ignore[arg-type]

    annex_i_safety = data.get("annex_i_safety_component", False)
    if not isinstance(annex_i_safety, bool):
        raise ChecklistError("invalid_answer", "'annex_i_safety_component' must be a boolean")

    annex_iii = data.get("annex_iii_area")
    if annex_iii is not None and (
        not isinstance(annex_iii, str) or annex_iii not in VALID_ANNEX_III_AREAS
    ):
        sanitized = str(annex_iii)[:50]
        raise ChecklistError("invalid_answer", f"Invalid Annex III area: '{sanitized}'")

    art6_3 = data.get("art6_3_exception", False)
    if not isinstance(art6_3, bool):
        raise ChecklistError("invalid_answer", "'art6_3_exception' must be a boolean")

    profiling = data.get("profiling", False)
    if not isinstance(profiling, bool):
        raise ChecklistError("invalid_answer", "'profiling' must be a boolean")

    interacts = data.get("interacts_with_persons", False)
    if not isinstance(interacts, bool):
        raise ChecklistError("invalid_answer", "'interacts_with_persons' must be a boolean")

    generates = data.get("generates_synthetic_content", False)
    if not isinstance(generates, bool):
        raise ChecklistError("invalid_answer", "'generates_synthetic_content' must be a boolean")

    emotion = data.get("emotion_or_biometric_categorisation", False)
    if not isinstance(emotion, bool):
        raise ChecklistError(
            "invalid_answer", "'emotion_or_biometric_categorisation' must be a boolean"
        )

    deepfake = data.get("deepfake", False)
    if not isinstance(deepfake, bool):
        raise ChecklistError("invalid_answer", "'deepfake' must be a boolean")

    gpai = data.get("gpai", False)
    if not isinstance(gpai, bool):
        raise ChecklistError("invalid_answer", "'gpai' must be a boolean")

    return Answers(
        role=role,
        art5=tuple(art5_list),
        annex_i_safety_component=annex_i_safety,
        annex_iii_area=annex_iii,  # type: ignore[arg-type]
        art6_3_exception=art6_3,
        profiling=profiling,
        interacts_with_persons=interacts,
        generates_synthetic_content=generates,
        emotion_or_biometric_categorisation=emotion,
        deepfake=deepfake,
        gpai=gpai,
    )


def _extract_article_sort_key(article_str: str, obl_id: str) -> tuple[int, int, str]:
    """Extract numerical key from article string (e.g., 'Art. 6(4)' -> (6, 4))."""
    m = re.search(r"(\d+)(?:\((\d+)\))?", article_str)
    if m:
        num = int(m.group(1))
        sub = int(m.group(2)) if m.group(2) else 0
        return (num, sub, obl_id)
    return (9999, 0, obl_id)


def assess(
    answers: Answers,
    *,
    table: Mapping[str, ObligationRow] = DEFAULT_TABLE,
) -> Assessment:
    """Assess compliance obligations based on structured answers."""
    notes: list[str] = []

    # 1. Check prohibited practices (Art. 5)
    if answers.art5:
        # Prohibited practices stop further assessment.
        # Art. 5 applies_from is the earliest date of selected points
        # a-h from 'art5', ba/bb from 'art5_ba_bb'
        dates: list[date] = []
        for p in answers.art5:
            row = table["art5_ba_bb"] if p in ("ba", "bb") else table["art5"]
            dates.append(row.applies_from)
        earliest = min(dates)
        art5_row = table["art5"]
        obligation = Obligation(
            id="art5",
            article=art5_row.article,
            title=art5_row.title,
            applies_from=earliest,
        )
        return Assessment(
            category="prohibited",
            obligations=(obligation,),
            notes=(),
        )

    # 2. Check high-risk
    # High-risk if annex_i_safety_component, or annex_iii_area set and not
    # (art6_3_exception and not profiling)
    annex_i_hr = answers.annex_i_safety_component
    annex_iii_hr = False
    if answers.annex_iii_area is not None:
        if answers.art6_3_exception and not answers.profiling:
            annex_iii_hr = False
        else:
            annex_iii_hr = True
            if answers.art6_3_exception and answers.profiling:
                notes.append(
                    "Art. 6(3): an Annex III system that performs profiling of natural persons "
                    "is always high-risk"
                )

    is_high_risk = annex_i_hr or annex_iii_hr
    hr_only_annex_i = annex_i_hr and not annex_iii_hr

    obligations: list[Obligation] = []

    # Non-prohibited results always include Art. 4
    art4_row = table["art4"]
    obligations.append(
        Obligation(
            id="art4",
            article=art4_row.article,
            title=art4_row.title,
            applies_from=art4_row.applies_from,
        )
    )

    def get_date(row: ObligationRow) -> date:
        if hr_only_annex_i and row.applies_from_annex_i is not None:
            return row.applies_from_annex_i
        return row.applies_from

    # Annex III with a valid exception -> art6_4 and art49_2 (providers only)
    if (
        answers.annex_iii_area is not None
        and answers.art6_3_exception
        and not answers.profiling
        and answers.role == "provider"
    ):
        r6_4 = table["art6_4"]
        obligations.append(
            Obligation(
                id="art6_4",
                article=r6_4.article,
                title=r6_4.title,
                applies_from=r6_4.applies_from,
            )
        )
        r49_2 = table["art49_2"]
        obligations.append(
            Obligation(
                id="art49_2",
                article=r49_2.article,
                title=r49_2.title,
                applies_from=r49_2.applies_from,
            )
        )

    if is_high_risk:
        if answers.role == "provider":
            # High-risk providers get art9, art10, art11, art12, art13, art14, art15, art17, art43,
            # art72, art73 plus art49 only for Annex III
            provider_ids = [
                "art9",
                "art10",
                "art11",
                "art12",
                "art13",
                "art14",
                "art15",
                "art17",
                "art43",
                "art72",
                "art73",
            ]
            if annex_iii_hr:
                provider_ids.append("art49")

            for oid in provider_ids:
                row = table[oid]
                obligations.append(
                    Obligation(
                        id=oid,
                        article=row.article,
                        title=row.title,
                        applies_from=get_date(row),
                    )
                )
        elif answers.role == "deployer":
            # deployers get art26 and art27
            for oid in ["art26", "art27"]:
                row = table[oid]
                obligations.append(
                    Obligation(
                        id=oid,
                        article=row.article,
                        title=row.title,
                        applies_from=get_date(row),
                    )
                )

    # Transparency (independent of high-risk):
    # providers: art50_1 (interacts_with_persons),
    #            art50_2 (generates_synthetic_content, with Art. 111(4) note)
    # deployers: art50_3 (emotion_or_biometric_categorisation), art50_4 (deepfake)
    has_art50 = False
    if answers.role == "provider":
        if answers.interacts_with_persons:
            r = table["art50_1"]
            obligations.append(
                Obligation(
                    id="art50_1", article=r.article, title=r.title, applies_from=r.applies_from
                )
            )
            has_art50 = True
        if answers.generates_synthetic_content:
            r = table["art50_2"]
            obligations.append(
                Obligation(
                    id="art50_2", article=r.article, title=r.title, applies_from=r.applies_from
                )
            )
            notes.append(
                "Art. 111(4): a generative system placed on the market before 2 August 2026 "
                "must comply with Art. 50(2) by 2 December 2026"
            )
            has_art50 = True
    elif answers.role == "deployer":
        if answers.emotion_or_biometric_categorisation:
            r = table["art50_3"]
            obligations.append(
                Obligation(
                    id="art50_3", article=r.article, title=r.title, applies_from=r.applies_from
                )
            )
            has_art50 = True
        if answers.deepfake:
            r = table["art50_4"]
            obligations.append(
                Obligation(
                    id="art50_4", article=r.article, title=r.title, applies_from=r.applies_from
                )
            )
            has_art50 = True

    # GPAI providers: art53 (with the Art. 111(3) note)
    if answers.role == "provider" and answers.gpai:
        r = table["art53"]
        obligations.append(
            Obligation(id="art53", article=r.article, title=r.title, applies_from=r.applies_from)
        )
        notes.append(
            "Art. 111(3): a general-purpose AI model placed on the market before 2 August 2025 "
            "must comply by 2 August 2027"
        )

    # Determine category: high_risk, else limited when any art50 id, else minimal
    if is_high_risk:
        category: Category = "high_risk"
    elif has_art50:
        category = "limited"
    else:
        category = "minimal"

    # Obligations sorted by article number then id
    obligations.sort(key=lambda o: _extract_article_sort_key(o.article, o.id))

    return Assessment(
        category=category,
        obligations=tuple(obligations),
        notes=tuple(notes),
    )


def render(a: Assessment, fmt: Literal["markdown", "json"]) -> str:
    """Render assessment in markdown or json format."""
    if fmt == "json":
        payload = {
            "category": a.category,
            "disclaimer": DISCLAIMER,
            "notes": list(a.notes),
            "obligations": [
                {
                    "applies_from": o.applies_from.isoformat(),
                    "article": o.article,
                    "id": o.id,
                    "title": o.title,
                }
                for o in a.obligations
            ],
        }
        return json.dumps(payload, indent=2, sort_keys=True)

    if fmt == "markdown":
        lines: list[str] = [
            DISCLAIMER,
            "",
            f"# EU AI Act Assessment: {a.category.replace('_', ' ').title()}",
            "",
        ]
        if a.notes:
            lines.append("## Notes")
            for note in a.notes:
                lines.append(f"- {note}")
            lines.append("")

        lines.append("## Obligations")
        for obl in a.obligations:
            lines.append(f"- [ ] {obl.article}: {obl.title} (from {obl.applies_from.isoformat()})")
        return "\n".join(lines)

    raise ChecklistError("invalid_answer", f"Unknown format: '{fmt}'")
