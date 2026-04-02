"""
Command-line interface for cyclesleep.

Usage:
    cyclesleep analyze <path_to_export.xml>
    cyclesleep analyze <path_to_export.xml> --output report.txt
"""

import argparse
import sys

from .parser import parse_export
from .analyzer import CycleSleepAnalyzer


def main():
    parser = argparse.ArgumentParser(
        prog="cyclesleep",
        description="Analyze menstrual cycle vs sleep quality from Apple Health data",
    )
    subparsers = parser.add_subparsers(dest="command")

    # analyze command
    analyze = subparsers.add_parser("analyze", help="Run full analysis on Apple Health export")
    analyze.add_argument("xml_path", help="Path to Apple Health exportación.xml")
    analyze.add_argument("--output", "-o", help="Save report to file")
    analyze.add_argument("--csv-dir", help="Also save intermediate CSVs to this directory")

    args = parser.parse_args()

    if args.command == "analyze":
        run_analyze(args)
    else:
        parser.print_help()


def run_analyze(args):
    print(f"Parsing {args.xml_path}...")
    data = parse_export(args.xml_path, progress_callback=lambda n: print(f"  {n:,} records...", end="\r"))
    print()

    for name, df in data.items():
        print(f"  {name}: {len(df):,} records")

    if args.csv_dir:
        from pathlib import Path
        csv_dir = Path(args.csv_dir)
        csv_dir.mkdir(parents=True, exist_ok=True)
        for name, df in data.items():
            path = csv_dir / f"{name}.csv"
            df.to_csv(path, index=False)
            print(f"  Saved {path}")

    print("\nAnalyzing...")
    analyzer = CycleSleepAnalyzer(data)
    report = analyzer.run()

    summary = report.summary()
    print()
    print(summary)

    if args.output:
        with open(args.output, "w") as f:
            f.write(summary)
        print(f"\nReport saved to {args.output}")


if __name__ == "__main__":
    main()
