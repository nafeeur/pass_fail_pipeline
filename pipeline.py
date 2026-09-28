"""Pass/Fail Check Pipeline - one generic check, daily + weekly.

AI assistance: the refactor of check_daily into a generic run_check(offset)
was suggested by Claude (Anthropic); I reviewed and tested it.
"""
import csv

INDEXES = {
    "SP500": "data/SP500.csv",
    "DJIA": "data/DJIA.csv",
    "DJCA": "data/DJCA.csv",
    "DJTA": "data/DJTA.csv",
    "DJUA": "data/DJUA.csv",
}

# offset = how many rows back to compare against (1 = previous day, 5 = ~1 week)
CHECKS = {
    "day_over_day": {"offset": 1, "threshold_pct": 1.0},
    "week_over_week": {"offset": 5, "threshold_pct": 5.0},
}


def load_series(filepath, column):
    """Return [(date, value), ...] sorted by date, skipping blank values."""
    rows = []
    with open(filepath, newline="") as f:
        for row in csv.DictReader(f):
            raw_value = row[column].strip()
            if not raw_value:
                continue  # market holiday: no reading for that date
            rows.append((row["observation_date"], float(raw_value)))
    rows.sort(key=lambda r: r[0])
    return rows


def run_check(ticker, check_name, series, offset, threshold_pct):
    """Compare each value to the one `offset` rows earlier."""
    breaches = []
    for i in range(offset, len(series)):
        date, value = series[i]
        compared_date, compared_value = series[i - offset]
        if compared_value == 0:
            continue
        pct_change = (value - compared_value) / compared_value * 100
        if abs(pct_change) > threshold_pct:
            breaches.append({
                "ticker": ticker,
                "check": check_name,
                "date": date,
                "value": value,
                "compared_date": compared_date,
                "compared_value": compared_value,
                "pct_change": round(pct_change, 4),
                "threshold_pct": threshold_pct,
            })
    return breaches


if __name__ == "__main__":
    for ticker, path in INDEXES.items():
        series = load_series(path, ticker)
        for name, cfg in CHECKS.items():
            found = run_check(ticker, name, series, cfg["offset"], cfg["threshold_pct"])
            print(f"{ticker} {name}: {len(found)}")
