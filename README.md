# eu-ai-act-checklist

[![PyPI version](https://img.shields.io/pypi/v/trysac-eu-ai-act-checklist)](https://pypi.org/project/trysac-eu-ai-act-checklist/)
[![License: MIT](https://img.shields.io/pypi/l/trysac-eu-ai-act-checklist)](LICENSE)
[![CI](https://github.com/Trysac/u190-eu-ai-act-checklist/actions/workflows/ci.yml/badge.svg)](https://github.com/Trysac/u190-eu-ai-act-checklist/actions/workflows/ci.yml)

EU AI Act checklist (2024/1689 as amended by 2026/1744): prohibited, high-risk, transparency and GPAI triggers mapped to obligations and dates

## Problem

Describe in two or three sentences the concrete problem this utility solves, who hits it, and what
they do today without it. Replace this paragraph when the first real feature lands.

## Install

```sh
pip install trysac-eu-ai-act-checklist
# or
uv add trysac-eu-ai-act-checklist
```

Requires Python 3.10 or newer. No runtime dependencies.

## Usage

```python
import eu_ai_act_checklist

# normalize() trims surrounding whitespace and lower-cases the text.
print(eu_ai_act_checklist.normalize("  Hello World "))  # -> "hello world"

# Blank input is rejected explicitly instead of returning an empty string.
try:
    eu_ai_act_checklist.normalize("   ")
except ValueError as exc:
    print(f"rejected: {exc}")
```

## Documentation

- [Architecture](docs/ARCHITECTURE.md) and [decisions](docs/decisions/)
- [Testing](docs/TESTING.md) and [security](docs/SECURITY.md)
- [Project record](docs/PROJECT.md) and [stack](docs/STACK.md)
- [Changelog](CHANGELOG.md) and [contributing guide](CONTRIBUTING.md)

## License

[MIT](LICENSE) (c) 2026 Miguel Gomez
