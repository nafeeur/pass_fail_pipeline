#!/usr/bin/env python3

"""Pass/Fail Check Pipeline.

Flags day-over-day and week-over-week price moves in stock market index
data that exceed configurable thresholds, and writes the flagged rows to CSV.

AI assistance: I generated almost all of this code using Claude Sonnet 5 and
my own custom built coding harness (github.com/nafeeur/MaskShift). I then
manually tested and verified myself. The initial design was mine, Including coming up with the config structure
and the decision to use only Python and JSON, so that no external libraries are needed.
"""

import argparse
import csv
import json
from pathlib import Path


def load_series(filepath, column):
    """Load (date, value) pairs from a CSV, sorted by date ascending.
    Rows with a blank value are skipped
    """
    rows = []
    with open(filepath, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            raw_value = row[column].strip()
            if not raw_value:
                continue
            rows.append((row["observation_date"], float(raw_value)))
    rows.sort(key=lambda r: r[0])
    return rows


def run_check(ticker, check_name, series, offset, threshold_pct):
    """Compare each value to the value `offset` rows earlier; return a
    flag record for every comparison whose absolute pct change exceeds
    threshold_pct.

    Day-over-day and week-over-week are the same operation with a
    different offset (1 row vs. 5 trading days ~= 1 calendar week), so both
    checks share this function instead of separate, near-duplicate
    implementations.
    """
    flags = []
    for i in range(offset, len(series)):
        date, value = series[i]
        compared_date, compared_value = series[i - offset]
        if compared_value == 0:
            continue
        pct_change = (value - compared_value) / compared_value * 100
        if abs(pct_change) > threshold_pct:
            flags.append({
                "ticker":s ticker,
                "check": check_name,
                "date": date,
                "value": value,
                "compared_date": compared_date,
                "compared_value": compared_value,
                "abs_change": round(value - compared_value, 4),
                "pct_change": round(pct_change, 4),
                "threshold_pct": threshold_pct,
            })
    return flags


def run_pipeline(config, base_dir):
    all_flags = []
    for ticker, index_cfg in config["indexes"].items():
        filepath = base_dir / index_cfg["file"]
        series = load_series(filepath, index_cfg["column"])
        for check_name, check_cfg in config["checks"].items():
            if not check_cfg.get("enabled", True):
                continue
            threshold = check_cfg.get("overrides", {}).get(ticker, check_cfg["default_threshold_pct"])
            all_flags.extend(
                run_check(ticker, check_name, series, check_cfg["offset"], threshold)
            )
    all_flags.sort(key=lambda f: (f["date"], f["ticker"], f["check"]))
    return all_flags


FIELDNAMES = [
    "ticker", "check", "date", "value",
    "compared_date", "compared_value", "abs_change", "pct_change", "threshold_pct",
]


def main():
    parser = argparse.ArgumentParser(description="Pass/Fail Check Pipeline")
    parser.add_argument("--config", default="config.json", help="Path to config JSON file")
    parser.add_argument("--output", default=None, help="Override the output CSV path from config")
    args = parser.parse_args()

    config_path = Path(args.config).resolve()
    with open(config_path) as f:
        config = json.load(f)
    base_dir = config_path.parent
    output_path = args.output or config.get("output_file", "results.csv")

    flags = run_pipeline(config, base_dir)

    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(flags)

    print(f"Checked {len(config['indexes'])} indexes across {len(config['checks'])} check types.")
    print(f"Flagged {len(flags)} rows -> {output_path}")


if __name__ == "__main__":
    main()