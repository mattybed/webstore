import argparse
import json
import subprocess
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pages", type=int, required=True)
    parser.add_argument("--expect", type=int, default=0)
    parser.add_argument("--outfile", type=Path, default=Path("/tmp/results.json"))
    args = parser.parse_args()

    cmd = [
        sys.executable,
        "scraper.py",
        "--keywords",
        "test",
        "--pages",
        str(args.pages),
        "--mode",
        "batch",
        "--output",
        str(args.outfile),
        "--sample-dir",
        "sample_data",
    ]

    subprocess.check_call(cmd)

    data = json.loads(Path(args.outfile).read_text())
    if len(data) < args.expect:
        print(f"Expected >= {args.expect} items, got {len(data)}")
        return 1
    print(f"Fetched {len(data)} items")
    return 0


if __name__ == "__main__":
    sys.exit(main())
