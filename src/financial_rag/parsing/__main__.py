"""Command-line entry point for the baseline PDF parser."""

import argparse
import logging
from pathlib import Path

from financial_rag.parsing.manifest import MANIFEST_FILENAME, write_manifest
from financial_rag.parsing.parser import (
    DEFAULT_ARTIFACTS_DIR,
    DEFAULT_INPUT_DIR,
    DEFAULT_OUTPUT_DIR,
    FinancialReportParser,
    ParserSettings,
    ParsingError,
)
from financial_rag.parsing.validation import (
    DEFAULT_DATASET_MANIFEST,
    ValidationError,
    validate_parsed_corpus,
    validate_source_corpus,
)


def _parse(args: argparse.Namespace, pdfs: list[Path]) -> tuple[int, int]:
    return FinancialReportParser(
        output_dir=args.output_dir,
        settings=ParserSettings(
            artifacts_dir=args.artifacts_dir,
            threads=args.threads,
        ),
    ).parse(pdfs)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Parse financial-report PDFs into JSON and retrieval text."
    )
    parser.add_argument("pdfs", nargs="*", type=Path)
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--artifacts-dir", type=Path, default=DEFAULT_ARTIFACTS_DIR)
    parser.add_argument(
        "--dataset-manifest",
        type=Path,
        default=DEFAULT_DATASET_MANIFEST,
    )
    parser.add_argument("--threads", type=int, default=4)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    try:
        if args.pdfs:
            succeeded, _ = _parse(args, list(args.pdfs))
        else:
            source = validate_source_corpus(args.input_dir, args.dataset_manifest)
            publication = args.output_dir / MANIFEST_FILENAME
            # Presence of this file certifies the outputs currently in the directory.
            publication.unlink(missing_ok=True)
            pdfs = [
                args.input_dir / document["filename"] for document in source["documents"]
            ]
            succeeded, _ = _parse(args, pdfs)
            parsed = validate_parsed_corpus(args.input_dir, args.output_dir, source)
            write_manifest(
                args.output_dir,
                parsed,
                dataset_manifest=args.dataset_manifest,
                corpus_fingerprint=source["corpus_fingerprint"],
            )
    except (OSError, ParsingError, ValidationError, ValueError) as error:
        logging.error("%s", error)
        return 1
    print(f"Parsed {succeeded} PDF(s) into {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
