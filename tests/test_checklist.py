"""Comprehensive tests for eu-ai-act-checklist."""

from __future__ import annotations

import json
from datetime import date
from io import StringIO
from pathlib import Path

import pytest

from eu_ai_act_checklist import (
    DEFAULT_TABLE,
    ChecklistError,
    ObligationRow,
    assess,
    load_answers,
    render,
)
from eu_ai_act_checklist.__main__ import main


def test_high_risk_provider_annex_iii() -> None:
    """assess(load_answers('{"role": "provider", "annex_iii_area": "employment"}')) returns category 'high_risk'..."""
    answers = load_answers('{"role": "provider", "annex_iii_area": "employment"}')
    res = assess(answers)
    assert res.category == "high_risk"
    expected_ids = [
        "art4",
        "art9",
        "art10",
        "art11",
        "art12",
        "art13",
        "art14",
        "art15",
        "art17",
        "art43",
        "art49",
        "art72",
        "art73",
    ]
    assert [o.id for o in res.obligations] == expected_ids
    for o in res.obligations:
        if o.id == "art4":
            assert o.applies_from == date(2025, 2, 2)
        else:
            assert o.applies_from == date(2027, 12, 2)


def test_prohibited_practices() -> None:
    """{"role": "provider", "art5": ["c"]} returns category 'prohibited' with obligation ids ['art5'] only..."""
    r1 = assess(load_answers('{"role": "provider", "art5": ["c"]}'))
    assert r1.category == "prohibited"
    assert [o.id for o in r1.obligations] == ["art5"]
    assert r1.obligations[0].applies_from == date(2025, 2, 2)

    r2 = assess(load_answers('{"role": "provider", "art5": ["ba"]}'))
    assert r2.category == "prohibited"
    assert [o.id for o in r2.obligations] == ["art5"]
    assert r2.obligations[0].applies_from == date(2026, 12, 2)

    r3 = assess(load_answers('{"role": "provider", "art5": ["bb", "c"]}'))
    assert r3.category == "prohibited"
    assert [o.id for o in r3.obligations] == ["art5"]
    assert r3.obligations[0].applies_from == date(2025, 2, 2)


def test_annex_iii_exception_and_profiling() -> None:
    """{"role": "provider", "annex_iii_area": "employment", "art6_3_exception": true} returns category 'minimal'..."""
    r1 = assess(
        load_answers(
            '{"role": "provider", "annex_iii_area": "employment", "art6_3_exception": true}'
        )
    )
    assert r1.category == "minimal"
    assert [o.id for o in r1.obligations] == ["art4", "art6_4", "art49_2"]
    assert r1.obligations[1].applies_from == date(2027, 12, 2)
    assert r1.obligations[2].applies_from == date(2026, 8, 2)

    r2 = assess(
        load_answers(
            '{"role": "provider", "annex_iii_area": "employment", "art6_3_exception": true, "profiling": true}'
        )
    )
    assert r2.category == "high_risk"
    assert (
        "Art. 6(3): an Annex III system that performs profiling of natural persons is always high-risk"
        in r2.notes
    )


def test_deployer_and_annex_i() -> None:
    """{"role": "deployer", "annex_iii_area": "education"} returns ids ['art4', 'art26', 'art27']..."""
    r1 = assess(load_answers('{"role": "deployer", "annex_iii_area": "education"}'))
    assert [o.id for o in r1.obligations] == ["art4", "art26", "art27"]
    assert r1.obligations[1].applies_from == date(2027, 12, 2)
    assert r1.obligations[2].applies_from == date(2027, 12, 2)

    r2 = assess(load_answers('{"role": "provider", "annex_i_safety_component": true}'))
    expected_annex_i_ids = [
        "art4",
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
    assert [o.id for o in r2.obligations] == expected_annex_i_ids
    for o in r2.obligations:
        if o.id != "art4":
            assert o.applies_from == date(2028, 8, 2)

    # With both Annex I and Annex III they use date(2027, 12, 2)
    r3 = assess(
        load_answers(
            '{"role": "provider", "annex_i_safety_component": true, "annex_iii_area": "education"}'
        )
    )
    for o in r3.obligations:
        if o.id != "art4":
            assert o.applies_from == date(2027, 12, 2)


def test_transparency_and_gpai() -> None:
    """{"role": "provider", "interacts_with_persons": true, "generates_synthetic_content": true}..."""
    r1 = assess(
        load_answers(
            '{"role": "provider", "interacts_with_persons": true, "generates_synthetic_content": true}'
        )
    )
    assert r1.category == "limited"
    assert [o.id for o in r1.obligations] == ["art4", "art50_1", "art50_2"]
    assert r1.obligations[1].applies_from == date(2026, 8, 2)
    assert r1.obligations[2].applies_from == date(2026, 8, 2)
    assert (
        "Art. 111(4): a generative system placed on the market before 2 August 2026 must comply with Art. 50(2) by 2 December 2026"
        in r1.notes
    )

    r2 = assess(load_answers('{"role": "deployer", "deepfake": true}'))
    assert "art50_4" in [o.id for o in r2.obligations]

    r3 = assess(load_answers('{"role": "provider", "gpai": true}'))
    assert "art53" in [o.id for o in r3.obligations]
    gpai_obl = next(o for o in r3.obligations if o.id == "art53")
    assert gpai_obl.applies_from == date(2025, 8, 2)
    assert (
        "Art. 111(3): a general-purpose AI model placed on the market before 2 August 2025 must comply by 2 August 2027"
        in r3.notes
    )


def test_validation_errors_and_limits() -> None:
    """load_answers('{"foo": 1}') raises ChecklistError with code 'unknown_question'..."""
    with pytest.raises(ChecklistError) as exc_info:
        load_answers('{"foo": 1}')
    assert exc_info.value.code == "unknown_question"

    with pytest.raises(ChecklistError) as exc_info:
        load_answers('{"role": "provider", "annex_iii_area": "sports"}')
    assert exc_info.value.code == "invalid_answer"

    with pytest.raises(ChecklistError) as exc_info:
        load_answers('{"role": "provider", "art5": ["i"]}')
    assert exc_info.value.code == "invalid_answer"

    # Size limits: 65_537 bytes raises input_too_large, 65_536 accepted
    large_valid_prefix = '{"role": "provider", "art5": []' + " " * (65_536 - 32) + "}"
    assert len(large_valid_prefix.encode("utf-8")) == 65_536
    ans = load_answers(large_valid_prefix)
    assert ans.role == "provider"

    too_large = large_valid_prefix + " "
    assert len(too_large.encode("utf-8")) == 65_537
    with pytest.raises(ChecklistError) as exc_info:
        load_answers(too_large)
    assert exc_info.value.code == "input_too_large"


def test_render_markdown_and_custom_table() -> None:
    """render(a, 'markdown') starts with preamble... and custom table behaves correctly."""
    a = assess(load_answers('{"role": "provider", "annex_iii_area": "employment"}'))
    md = render(a, "markdown")
    assert md.startswith(
        "Technical aid, not legal advice. Based on Regulation (EU) 2024/1689 as amended by Regulation (EU) 2026/1744 (dates checked 2026-11-07); check later amendments.\n"
    )
    assert "- [ ] Art. 9: Risk management system (from 2027-12-02)" in md

    # assess(answers, table=custom) with art9 applies_from date(2028, 1, 15) renders '(from 2028-01-15)'
    custom_table = dict(DEFAULT_TABLE)
    custom_table["art9"] = ObligationRow(
        article="Art. 9",
        title="Risk management system",
        applies_from=date(2028, 1, 15),
    )
    a_custom = assess(
        load_answers('{"role": "provider", "annex_iii_area": "employment"}'), table=custom_table
    )
    md_custom = render(a_custom, "markdown")
    assert "(from 2028-01-15)" in md_custom


def test_cli(tmp_path: Path) -> None:
    """CLI main(['answers.json', '--format', 'json']) prints JSON and returns 0, or 2 for ChecklistError."""
    answers_dir = tmp_path / "data"
    answers_dir.mkdir(parents=True, exist_ok=True)
    answers_file = answers_dir / "answers.json"
    answers_file.write_text(
        '{"role": "provider", "annex_iii_area": "employment"}', encoding="utf-8"
    )

    # Test JSON CLI output
    code = main([str(answers_file), "--format", "json"])
    assert code == 0

    # Test error output
    bad_file = answers_file.parent / "bad.json"
    bad_file.write_text('{"foo": 1}', encoding="utf-8")
    code_err = main([str(bad_file)])
    assert code_err == 2

    # Non-existent file
    code_missing = main([str(answers_file.parent / "nonexistent.json")])
    assert code_missing == 2


def test_additional_edge_cases(monkeypatch: pytest.MonkeyPatch) -> None:
    """Exercise additional branches: invalid json, bad types, stdin, render json."""
    with pytest.raises(ChecklistError) as exc:
        load_answers("not json")
    assert exc.value.code == "invalid_json"

    with pytest.raises(ChecklistError) as exc:
        load_answers("[1, 2, 3]")
    assert exc.value.code == "invalid_json"

    with pytest.raises(ChecklistError) as exc:
        load_answers('{"role": "invalid"}')
    assert exc.value.code == "invalid_answer"

    with pytest.raises(ChecklistError) as exc:
        load_answers('{"role": "provider", "art5": "not_a_list"}')
    assert exc.value.code == "invalid_answer"

    for field in [
        "annex_i_safety_component",
        "art6_3_exception",
        "profiling",
        "interacts_with_persons",
        "generates_synthetic_content",
        "emotion_or_biometric_categorisation",
        "deepfake",
        "gpai",
    ]:
        with pytest.raises(ChecklistError) as exc:
            load_answers(f'{{"role": "provider", "{field}": "not_a_bool"}}')
        assert exc.value.code == "invalid_answer"

    # Deployer with emotion_or_biometric_categorisation
    r = assess(load_answers('{"role": "deployer", "emotion_or_biometric_categorisation": true}'))
    assert r.category == "limited"
    assert "art50_3" in [o.id for o in r.obligations]

    # Deployer high risk with Annex I safety component only
    r_dep_annex_i = assess(load_answers('{"role": "deployer", "annex_i_safety_component": true}'))
    assert r_dep_annex_i.category == "high_risk"
    assert r_dep_annex_i.obligations[1].applies_from == date(2028, 8, 2)

    # JSON render format
    js = render(r, fmt="json")
    loaded = json.loads(js)
    assert loaded["category"] == "limited"
    assert len(loaded["obligations"]) >= 2

    # Invalid format in render
    with pytest.raises(ChecklistError):
        render(r, fmt="yaml")  # type: ignore[arg-type]

    # CLI with stdin
    monkeypatch.setattr("sys.stdin", StringIO('{"role": "provider"}'))
    assert main([]) == 0
