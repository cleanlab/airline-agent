import datetime
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any, TypedDict

from append_test_results import TIMESTAMP_FORMAT

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT_DIR / "stability_data.json"
REPORT_FILE = ROOT_DIR / "README.md"

REPORT_WINDOW_DAYS = 10


class TestSummary(TypedDict):
    failures: int
    passes: int
    question: str
    last_fail: dict[str, Any] | None


def main() -> None:
    if not DATA_FILE.exists():
        print("No stability_data.json found — skipping report.")
        return

    today = datetime.datetime.now(datetime.UTC).date()
    cutoff = today - datetime.timedelta(days=REPORT_WINDOW_DAYS)

    with open(DATA_FILE) as f:
        logs = json.load(f)

    recent = [
        x
        for x in logs
        if datetime.datetime.strptime(x["timestamp"], TIMESTAMP_FORMAT).replace(tzinfo=datetime.UTC).date() >= cutoff
    ]

    latest_questions: dict[str, tuple[str, datetime.datetime]] = {}
    for entry in recent:
        test_name = entry["test_name"]
        if entry.get("stdout"):
            matches = re.findall(r"^QUESTION:\s*(.+)$", entry["stdout"], flags=re.MULTILINE)
            for question_text in matches:
                question = question_text.strip()
                entry_time = datetime.datetime.strptime(entry["timestamp"], TIMESTAMP_FORMAT).replace(
                    tzinfo=datetime.UTC
                )

                if test_name not in latest_questions:
                    latest_questions[test_name] = (question, entry_time)
                else:
                    _, existing_time = latest_questions[test_name]
                    if entry_time > existing_time:
                        latest_questions[test_name] = (question, entry_time)

    summary: defaultdict[str, TestSummary] = defaultdict(
        lambda: {"failures": 0, "passes": 0, "question": "", "last_fail": None}
    )

    for entry in recent:
        test_name = entry["test_name"]

        entry_question = None
        if entry.get("stdout"):
            matches = re.findall(r"^QUESTION:\s*(.+)$", entry["stdout"], flags=re.MULTILINE)
            if matches:
                entry_question = matches[0].strip()

        if test_name in latest_questions:
            latest_question, _ = latest_questions[test_name]
            # Skip entries with old questions, but allow entries without questions
            if entry_question is not None and entry_question != latest_question:
                continue

        outcome = entry["outcome"]
        if outcome == "failed":
            summary[test_name]["failures"] += 1
            summary[test_name]["last_fail"] = entry
        elif outcome == "passed":
            summary[test_name]["passes"] += 1

        if entry_question:
            summary[test_name]["question"] = entry_question

    with open(REPORT_FILE, "w") as md:
        md.write(f"### 🧩 Stability Summary ({today})\n")
        md.write(f"*Aggregated from the last {REPORT_WINDOW_DAYS} days ({cutoff} → {today})*\n\n")

        if not recent:
            md.write(f"⚠️ No recent tests ran in the last {REPORT_WINDOW_DAYS} days.\n")
        else:
            flaky = {k: v for k, v in summary.items() if v["failures"] > 0}
            if not flaky:
                md.write(f"✅ All tests passed consistently in the last {REPORT_WINDOW_DAYS} days.\n")
            else:
                md.write("#### ❗ Flaky / Failing Tests\n")
                md.write("| Test | Failures | Passes | Failure Rate |\n")
                md.write("|------|-----------|--------|--------------|\n")

                for test_name, data in sorted(flaky.items()):
                    total = data["failures"] + data["passes"]
                    rate = (data["failures"] / total) * 100 if total else 0
                    md.write(f"| `{test_name}` | {data['failures']} | {data['passes']} | {rate:.0f}% |\n")

                md.write("\n---\n\n#### 🔍 Failure Details\n\n")

                for test_name, data in sorted(flaky.items()):
                    entry = data["last_fail"]
                    md.write(f"##### `{test_name}`\n")
                    md.write(f"**Failures:** {data['failures']} times\n")
                    if data["question"]:
                        md.write(f"**Question:** {data['question']}\n")
                    if entry and entry.get("error_msg"):
                        log = entry["error_msg"].strip()
                        md.write("\n<details>\n")
                        md.write("<summary><strong>View full failure log</strong></summary>\n\n")
                        md.write("\n\n```\n")
                        md.write(log)
                        md.write("\n```\n")
                        md.write("</details>\n\n---\n\n")

    print(f"Updated {REPORT_FILE}")


if __name__ == "__main__":
    main()
