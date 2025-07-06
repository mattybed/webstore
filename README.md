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

To run without network access, use the provided sample pages:

```bash
python scraper.py --keywords test --pages 3 --sample-dir sample_data --output results.json
```

Run smoke test:

```bash
make smoke
```

Run end-to-end test:

```bash
make e2e
```
