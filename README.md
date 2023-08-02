# Extract DailyMed SPL

Extracting the indication from the SPLs (Structured Product Labeling) that are coming from DailyMed dataset.

## Install

Create and activate virtual env

```bash
python -m venv .venv
source .venv/bin/activate
```

Install

```bash
pip install -e .
```

## Run

With hatch

```bash
hatch run python src/dm_parser.py
```

Without hatch

```bash
python src/dm_parser.py
```
