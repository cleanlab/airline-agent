#!/usr/bin/env python3
import argparse
import datetime
import json
from pathlib import Path

TIMESTAMP_FORMAT = "%d-%m-%y %H:%M:%S"

RETENTION_WINDOW_DAYS = 10


def main() -> None:
    parser = argparse.ArgumentParser(description="Append test results to stability data")
    parser.add_argument("marker", help="Marker identifier for the test run")
    args = parser.parse_args()

    marker = args.marker
    report_file = Path(f"results/report-{marker}.json")
    output_file = Path("stability_data.json")

    if not report_file.exists():
        print(f"No report file found at {report_file}")
        return

    with report_file.open() as f:
        report = json.load(f)

    timestamp = datetime.datetime.fromtimestamp(report["created"], tz=datetime.UTC).strftime(TIMESTAMP_FORMAT)
    tests = report.get("tests", [])
    if not tests:
        print(f"No tests found in {report_file}")
        return

    today = datetime.datetime.now(datetime.UTC).date()
    cutoff = today - datetime.timedelta(days=RETENTION_WINDOW_DAYS)

    if output_file.exists():
        with output_file.open() as f:
            all_existing_entries = json.load(f)
        existing_entries = [
            entry
            for entry in all_existing_entries
            if datetime.datetime.strptime(entry["timestamp"], TIMESTAMP_FORMAT).replace(tzinfo=datetime.UTC).date()
            >= cutoff
        ]
    else:
        existing_entries = []

    new_entries = []
    for test in tests:
        call = test.get("call", {})
        entry = {
            "timestamp": timestamp,
            "marker": marker,
            "test_name": test["nodeid"],
            "outcome": test["outcome"],
            "stdout": call.get("stdout", ""),
            "error_msg": call.get("crash", {}).get("message", ""),
        }
        new_entries.append(entry)

    existing_entries.extend(new_entries)
    with output_file.open("w") as f:
        json.dump(existing_entries, f, indent=2)

    print(f"Appended {len(new_entries)} results to {output_file}")


if __name__ == "__main__":
    main()
