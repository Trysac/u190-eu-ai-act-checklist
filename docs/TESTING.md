# Testing

Tests are located in `tests/` and executed via `pytest`.

- `tests/test_checklist.py`: Verifies the core `assess` logic against acceptance criteria, including prohibited practice logic, high-risk scoring, transparency triggers, and GPAI obligations.
- `tests/test_eu_ai_act_checklist.py`: Tests the public API for versioning and semver compliance.
- **Coverage**: Includes boundary checks (max input size), validation errors (unknown keys, bad types), and rendering formats (JSON/markdown).