"""Command-line entry point for the baseline PDF parser."""

import argparse
import logging
from pathlib import Path

from financial_rag.parsing.parser import (
    DEFAULT_ARTIFACTS_DIR,
    DEFAULT_INPUT_DIR,
    DEFAULT_OUTPUT_DIR,
    FinancialReportParser,
    ParserSettings,
    ParsingError,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Parse financial-report PDFs into JSON and retrieval text."
    )
    parser.add_argument("pdfs", nargs="*", type=Path)
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--artifacts-dir", type=Path, default=DEFAULT_ARTIFACTS_DIR)
    parser.add_argument("--threads", type=int, default=4)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    pdfs = args.pdfs or sorted(args.input_dir.glob("*.pdf"))
    try:
        succeeded, _ = FinancialReportParser(
            output_dir=args.output_dir,
            settings=ParserSettings(
                artifacts_dir=args.artifacts_dir,
                threads=args.threads,
            ),
        ).parse(pdfs)
    except (OSError, ParsingError, ValueError) as error:
        logging.error("%s", error)
        return 1
    print(f"Parsed {succeeded} PDF(s) into {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
