"""CLI entrypoint for eu_ai_act_checklist."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from eu_ai_act_checklist.checklist import ChecklistError, assess, load_answers, render


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI.

    Returns 0 on success, 2 on ChecklistError, and standard exit codes for CLI arg errors.
    """
    parser = argparse.ArgumentParser(
        prog="eu-ai-act-checklist",
        description="EU AI Act obligation assessment checklist tool.",
    )
    parser.add_argument(
        "file",
        nargs="?",
        default="-",
        help="Path to JSON answers file, or '-' for stdin (default: '-')",
    )
    parser.add_argument(
        "--format",
        "-f",
        dest="fmt",
        choices=["markdown", "json"],
        default="markdown",
        help="Output format (markdown or json, default: markdown)",
    )

    args = parser.parse_args(argv)

    try:
        if args.file == "-":
            content = sys.stdin.read()
        else:
            path = Path(args.file)
            if not path.is_file():
                sys.stderr.write(f"File not found: {args.file}\n")
                return 2
            content = path.read_text(encoding="utf-8")

        answers = load_answers(content)
        assessment = assess(answers)
        output = render(assessment, fmt=args.fmt)
        print(output)
        return 0
    except ChecklistError as exc:
        sys.stderr.write(f"ChecklistError [{exc.code}]: {exc}\n")
        return 2


if __name__ == "__main__":
    sys.exit(main())
