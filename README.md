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

## Legal Disclaimer

Technical aid, not legal advice. Based on Regulation (EU) 2024/1689 as amended by Regulation (EU) 2026/1744. Check [Regulation (EU) 2024/1689](https://eur-lex.europa.eu/eli/reg/2024/1689/oj/eng) and [Regulation (EU) 2026/1744](https://eur-lex.europa.eu/eli/reg/2026/1744/oj/eng) for definitive legal interpretation.