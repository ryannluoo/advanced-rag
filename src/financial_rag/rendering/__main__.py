"""Command-line entry point for rendering parsed reports."""

import argparse
import logging
from pathlib import Path

from financial_rag.rendering.renderer import (
    DEFAULT_INPUT_DIR,
    DEFAULT_OUTPUT_DIR,
    RenderingError,
    render_directory,
    render_paths,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Render parsed financial reports into markdown pages."
    )
    parser.add_argument("reports", nargs="*", type=Path)
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    try:
        if args.reports:
            count = render_paths(args.reports, args.output_dir)
        else:
            count = render_directory(args.input_dir, args.output_dir)
    except (OSError, RenderingError) as error:
        logging.error("%s", error)
        return 1
    print(f"Rendered {count} report(s) into {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
