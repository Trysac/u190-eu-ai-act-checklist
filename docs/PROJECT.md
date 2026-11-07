# Project Record

## Objective
Automated technical compliance obligation checklist tool for CI and engineering workflows.

## Scope
- Mapping prohibited practices (Art. 5).
- High-risk evaluation for Annex I and Annex III systems.
- Transparency obligations (Art. 50).
- GPAI provider obligations (Art. 53).

## Out-of-Scope
- Legal interpretation of exceptions.
- Sector-specific legislation.
- Conformity assessment templates.
- National execution rules.
- SME simplifications.
- Legacy systems under Art. 111(2).
- Amendments after 2026-11-07.

## Factory run u190 (measured from API usage)

| Phase | Model | Batch | Input | Output | Cache write | Cache read | Cost (USD) |
|---|---|---|---|---|---|---|---|
| generation | gemini-3.8-flash | yes | 5626 | 13276 | 0 | 0 | 0.0270 |
| fix-1 | gemini-3.8-flash | no | 63107 | 3032 | 0 | 402173 | 0.0889 |
| fix-2 | gemini-3.8-flash | no | 89301 | 1156 | 0 | 670838 | 0.1216 |
| fix-3 | gemini-3.8-flash | no | 31967 | 850 | 0 | 101595 | 0.0348 |
| audit | gemini-3.1-flash-lite | no | 50711 | 286 | 0 | 177453 | 0.0175 |
| fix-4 | gemini-3.8-flash | no | 45848 | 304 | 0 | 247825 | 0.0541 |
| docs | gemini-3.1-flash-lite | no | 111409 | 1522 | 0 | 0 | 0.0301 |

Total: $0.3741. Prices: Anthropic list prices.
