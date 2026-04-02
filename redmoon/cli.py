"""
Command-line interface for redmoon.

Usage:
    redmoon analyze <path_to_export.xml>
    redmoon analyze <path_to_export.xml> --output report.txt
"""

from __future__ import annotations

import argparse
import logging
import sys

from .parser import parse_export
from .analyzer import CycleSleepAnalyzer

logger = logging.getLogger("redmoon")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="redmoon",
        description="Analyze menstrual cycle vs sleep quality from Apple Health data",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable debug logging",
    )
    subparsers = parser.add_subparsers(dest="command")

    # analyze command
    analyze = subparsers.add_parser("analyze", help="Run full analysis on Apple Health export")
    analyze.add_argument("xml_path", help="Path to Apple Health exportación.xml")
    analyze.add_argument("--output", "-o", help="Save report to file")
    analyze.add_argument("--csv-dir", help="Also save intermediate CSVs to this directory")

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    if args.command == "analyze":
        run_analyze(args)
    else:
        parser.print_help()


def run_analyze(args: argparse.Namespace) -> None:
    logger.info("Parsing %s...", args.xml_path)
    data = parse_export(
        args.xml_path,
        progress_callback=lambda n: print(f"  {n:,} records...", end="\r"),
    )
    print()

    for name, df in data.items():
        logger.info("  %s: %s records", name, f"{len(df):,}")

    if args.csv_dir:
        from pathlib import Path
        csv_dir = Path(args.csv_dir)
        csv_dir.mkdir(parents=True, exist_ok=True)
        for name, df in data.items():
            path = csv_dir / f"{name}.csv"
            df.to_csv(path, index=False)
            logger.info("  Saved %s", path)

    logger.info("Analyzing...")
    analyzer = CycleSleepAnalyzer(data)
    report = analyzer.run()

    summary = report.summary()
    print()
    print(summary)

    if args.output:
        with open(args.output, "w") as f:
            f.write(summary)
        logger.info("Report saved to %s", args.output)


if __name__ == "__main__":
    main()
