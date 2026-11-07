# trysac-eu-ai-act-checklist

Teams building AI features hear that the EU AI Act applies but cannot tell which obligations concern their system, from when, or whether they act as provider or deployer, and the 2026 Digital Omnibus moved most high-risk dates. Long legal summaries do not turn into an engineering checklist. This library maps prohibited, high-risk, transparency, and GPAI triggers to specific obligations.

## Installation

```bash
pip install trysac-eu-ai-act-checklist
```

## Usage

```python
from eu_ai_act_checklist import assess, load_answers, render

# Provide a JSON-compatible string of answers
answers = load_answers('{"role": "provider", "annex_iii_area": "employment"}')
# Calculate triggered obligations
assessment = assess(answers)
# Output as markdown or json
print(render(assessment, fmt="markdown"))
```

## API Summary

- `load_answers(text: str, *, max_bytes: int = 65_536) -> Answers`: Parses input JSON; raises `ChecklistError` if size exceeds `max_bytes`, JSON is invalid, or schema violations occur.
- `assess(answers: Answers, *, table: Mapping[str, ObligationRow] = DEFAULT_TABLE) -> Assessment`: Logic processor evaluating risk categories and application dates.
- `render(a: Assessment, fmt: Literal["markdown", "json"]) -> str`: Formats the result.
- Error handling: `ChecklistError` covers `input_too_large`, `invalid_json`, `unknown_question`, `invalid_answer`.

## Why this tool?

Unlike static legal summaries, this is a versioned engineering library that allows compliance mapping within CI/CD pipelines. It treats regulation as data, making compliance logic reproducible and unit-testable.

[Security Policy](docs/SECURITY.md)

## Application dates

`DEFAULT_TABLE` holds the date each obligation applies from, as set by Article 113 of Regulation (EU) 2024/1689 after Regulation (EU) 2026/1744 (in force 27 July 2026; dates checked 2026-11-07). The table is data: pass `table=` to `assess` when a later amendment moves a date.

| Obligation | Applies from |
|---|---|
| Art. 4 AI literacy measures, Art. 5(1)(a)-(h) prohibited practices | 2025-02-02 |
| Art. 53 general-purpose AI models (models placed before 2025-08-02: by 2027-08-02) | 2025-08-02 |
| Art. 50 transparency (Art. 50(2) for generative systems placed before 2026-08-02: by 2026-12-02); Art. 49(2) registration of an Art. 6(3) exception | 2026-08-02 |
| Art. 5(1)(ba) and (bb), added by Regulation (EU) 2026/1744 | 2026-12-02 |
| High-risk obligations (Arts 6(4), 9-15, 17, 26, 27, 43, 49, 72, 73), Annex III systems | 2027-12-02 |
| The same obligations for systems that are high-risk only through Annex I | 2028-08-02 |

Articles 43, 49, 72 and 73 fall outside Article 113(c), so on a literal reading they apply from 2026-08-02. They bind a provider through Article 16, whose obligations apply from the high-risk dates above, so the table uses those dates. This reading is not confirmed by official guidance; override the rows if your counsel reads it differently.

## Legal Disclaimer

Technical aid, not legal advice. Based on Regulation (EU) 2024/1689 as amended by Regulation (EU) 2026/1744. Check [Regulation (EU) 2024/1689](https://eur-lex.europa.eu/eli/reg/2024/1689/oj/eng) and [Regulation (EU) 2026/1744](https://eur-lex.europa.eu/eli/reg/2026/1744/oj/eng) for definitive legal interpretation.