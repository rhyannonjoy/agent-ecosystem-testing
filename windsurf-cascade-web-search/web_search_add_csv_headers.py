#!/usr/bin/env python3
"""
Add headers to an existing results CSV that was written without them.
Run once per CSV file that is missing headers.

Usage:
    python web_search_add_csv_headers.py --track interpreted
    python web_search_add_csv_headers.py --track raw
    python web_search_add_csv_headers.py --track explicit
"""

import csv
import argparse
from dataclasses import fields
from pathlib import Path
from web_search_testing_framework import TestResult


def add_headers(track: str):
    csv_path = Path(f"results/cascade-{track}/results.csv")

    if not csv_path.exists():
        print(f"No results.csv found at {csv_path}")
        return

    header = [f.name for f in fields(TestResult)]

    with open(csv_path, "r") as f:
        existing = f.read()

    if existing.startswith(header[0]):
        print(f"Headers already present in {csv_path}, nothing to do.")
        return

    with open(csv_path, "w") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        f.write(existing)

    print(f"✓ Headers added to {csv_path}")


def main():
    parser = argparse.ArgumentParser(description="Add headers to a results CSV missing them")
    parser.add_argument(
        "--track",
        type=str,
        choices=["interpreted", "raw", "explicit"],
        required=True,
        help="Track whose results.csv needs headers added",
    )
    args = parser.parse_args()
    add_headers(args.track)


if __name__ == "__main__":
    main()