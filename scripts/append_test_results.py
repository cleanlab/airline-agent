#!/usr/bin/env python3
import argparse
import datetime
import json
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Append test results to stability data")
    parser.add_argument("marker", help="Marker identifier for the test run")
    args = parser.parse_args()

    marker = args.marker
    report_file = Path(f"results/report-{marker}.json")
    output_file = Path("stability_data.json")

    if not report_file.exists():
        print(f"No report file found at {report_file}")
        sys.exit(0)

    with report_file.open() as f:
        report = json.load(f)

    timestamp = datetime.datetime.fromtimestamp(report["created"], tz=datetime.UTC).strftime("%d-%m-%y %H:%M:%S")
    tests = report.get("tests", [])
    if not tests:
        print(f"No tests found in {report_file}")
        sys.exit(0)

    entries = []
    for test in tests:
        call = test.get("call", {})
        entry = {
            "timestamp": timestamp,
            "marker": marker,
            "test_name": test["nodeid"],
            "outcome": test["outcome"],
            "stdout": call.get("stdout", ""),
            "stderr": call.get("stderr", ""),
        }
        entries.append(entry)

    with output_file.open("a") as f:
        for entry in entries:
            f.write(json.dumps(entry) + "\n")

    print(f"Appended {len(entries)} results to {output_file}")


if __name__ == "__main__":
    main()
