# Watchcount Scraper

Command-line tool to fetch listing data directly from Watchcount.

## Setup

```bash
make install
```

## Usage

```bash
python scraper.py --keywords "garden planter" --pages 3 --min-price 15 --site EBAY_GB --mode batch --output results.json
```

Run smoke test:

```bash
make smoke
```

Run end-to-end test:

```bash
make e2e
```
