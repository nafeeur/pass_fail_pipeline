# Pass/Fail Check Pipeline

Reads US stock index prices from CSV files and flags big price moves:

- **Day-over-day:** change greater than 1%
- **Week-over-week:** change greater than 5% (compared to 5 trading days earlier)

Flagged rows are written to `results.csv`.

## Setup

Requires Python 3.8+. No libraries to install (standard library only).

Project layout:

```
pipeline.py
config.json
data/
  SP500.csv  DJIA.csv  DJCA.csv  DJTA.csv  DJUA.csv
```

## Run

```bash
python3 pipeline.py --config config.json
```

Optional: `--output my_results.csv` to choose a different output file.

## Configuration

Edit `config.json` (no code changes needed):

- `enabled`: turn a check on or off
- `default_threshold_pct`: threshold for all indexes
- `overrides`: a different threshold for one index, e.g. `"SP500": 1.5`
- `offset`: how many trading days back to compare (1 = day, 5 = week)

## Output

`results.csv` has one row per flagged move:

| column | meaning |
|---|---|
| ticker | index symbol (e.g. SP500) |
| check | which check flagged it |
| date | date of the value |
| value | value on that date |
| compared_date | date it was compared against |
| compared_value | value on that earlier date |
| abs_change | difference (`value - compared_value`) |
| pct_change | percent change |
| threshold_pct | threshold that was applied |

## Design notes

- One `run_check` function handles both checks, only the `offset` differs.
- Config is a static JSON file, so thresholds can change without touching the code.
- Blank rows in the data are skipped.

## AI assistance

I generated almost all of this code using Claude Sonnet 5 and my own custom-built coding harness (github.com/nafeeur/MaskShift). I then manually tested and verified it myself. The initial design was mine, including the config structure and the decision to use only Python and JSON, so that no external libraries are needed. Config validation was not implemented in this version.