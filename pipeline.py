"""Pass/Fail Check Pipeline - step 2: load one index file."""
import csv
 
 
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
 
 
if __name__ == "__main__":
    series = load_series("data/SP500.csv", "SP500")
    print(f"Loaded {len(series)} rows. First: {series[0]}, last: {series[-1]}")
 
