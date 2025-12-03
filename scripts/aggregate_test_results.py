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
MAX_QUESTION_DISPLAY_LENGTH = 80


class TestSummary(TypedDict):
    failures: int
    passes: int
    question: str
    test_names: list[str]
    last_fail: dict[str, Any] | None


def extract_question(entry: dict) -> str | None:
    """Extract question from entry stdout, return None if not found."""
    if not entry.get("stdout"):
        return None
    matches = re.findall(r"^QUESTION:\s*(.+)$", entry["stdout"], flags=re.MULTILINE)
    if matches:
        return matches[0].strip()
    return None


def is_timeout_failure(entry: dict) -> bool:
    """Check if entry represents a timeout/connection failure."""
    stdout = entry.get("stdout", "").lower()
    error_msg = entry.get("error_msg", "").lower()
    return "timeout" in stdout or "timeout" in error_msg


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

    recent = [x for x in recent if not is_timeout_failure(x)]

    latest_questions: dict[str, tuple[str, datetime.datetime]] = {}
    for entry in recent:
        test_name = entry["test_name"]
        entry_question = extract_question(entry)

        if entry_question:
            entry_time = datetime.datetime.strptime(entry["timestamp"], TIMESTAMP_FORMAT).replace(tzinfo=datetime.UTC)

            if test_name not in latest_questions:
                latest_questions[test_name] = (entry_question, entry_time)
            else:
                _, existing_time = latest_questions[test_name]
                if entry_time > existing_time:
                    latest_questions[test_name] = (entry_question, entry_time)

    summary: dict[str, defaultdict[str, TestSummary]] = {
        "main": defaultdict(lambda: {"failures": 0, "passes": 0, "question": "", "test_names": [], "last_fail": None}),
        "additional": defaultdict(
            lambda: {"failures": 0, "passes": 0, "question": "", "test_names": [], "last_fail": None}
        ),
    }

    for entry in recent:
        test_name = entry["test_name"]
        entry_question = extract_question(entry)
        marker = entry.get("marker", "main")

        if test_name in latest_questions:
            latest_question, _ = latest_questions[test_name]
            if entry_question is not None and entry_question != latest_question:
                continue

        group_key = entry_question if entry_question else test_name

        if marker not in summary:
            marker = "main"

        outcome = entry["outcome"]
        if outcome == "failed":
            summary[marker][group_key]["failures"] += 1
            if summary[marker][group_key]["last_fail"] is None:
                summary[marker][group_key]["last_fail"] = entry
        elif outcome == "passed":
            summary[marker][group_key]["passes"] += 1

        if entry_question:
            summary[marker][group_key]["question"] = entry_question
        if test_name not in summary[marker][group_key]["test_names"]:
            summary[marker][group_key]["test_names"].append(test_name)

    with open(REPORT_FILE, "w") as md:
        md.write(f"### 🧩 Stability Summary ({today})\n")
        md.write(f"*Aggregated from the last {REPORT_WINDOW_DAYS} days ({cutoff} → {today})*\n\n")

        if not recent:
            md.write(f"⚠️ No recent tests ran in the last {REPORT_WINDOW_DAYS} days.\n")
        else:
            main_tests = summary["main"]
            main_flaky = {k: v for k, v in main_tests.items() if v["failures"] > 0}

            additional_tests = summary["additional"]
            additional_flaky = {k: v for k, v in additional_tests.items() if v["failures"] > 0}

            has_main_issues = len(main_flaky) > 0
            has_additional_issues = len(additional_flaky) > 0

            if not has_main_issues and not has_additional_issues:
                md.write(f"✅ All tests passed consistently in the last {REPORT_WINDOW_DAYS} days.\n")
            else:
                if has_main_issues:
                    md.write("#### ❗ Main Tests (Must be 100% Stable)\n")
                    md.write("| Question | Failures | Passes | Failure Rate |\n")
                    md.write("|----------|----------|--------|--------------|\n")

                    for question_key, data in sorted(main_flaky.items()):
                        total = data["failures"] + data["passes"]
                        rate = (data["failures"] / total) * 100 if total else 0
                        display_question = data["question"] if data["question"] else question_key
                        if len(display_question) > MAX_QUESTION_DISPLAY_LENGTH:
                            display_question = display_question[: MAX_QUESTION_DISPLAY_LENGTH - 3] + "..."
                        md.write(f"| `{display_question}` | {data['failures']} | {data['passes']} | {rate:.0f}% |\n")

                    md.write("\n---\n\n#### 🔍 Main Test Failure Details\n\n")

                    for question_key, data in sorted(main_flaky.items()):
                        entry = data["last_fail"]
                        display_question = data["question"] if data["question"] else question_key
                        md.write(f"##### `{display_question}`\n\n")
                        md.write(f"**Failures:** {data['failures']} times\n\n")

                        if data["test_names"]:
                            test_names_str = ", ".join(f"`{tn}`" for tn in sorted(data["test_names"]))
                            md.write(f"**Test Names:** {test_names_str}\n\n")

                        if entry and entry.get("error_msg"):
                            log = entry["error_msg"].strip()
                            md.write("\n<details>\n")
                            md.write("<summary><strong>View full failure log</strong></summary>\n\n")
                            md.write("\n\n```\n")
                            md.write(log)
                            md.write("\n```\n")
                            md.write("</details>\n\n---\n\n")

                    md.write("\n")
                else:
                    md.write("#### ✅ Main Tests\n")
                    md.write("All main tests passed consistently (100% stable).\n\n")

                if has_additional_issues:
                    md.write("#### 📊 Additional Tests (Some Instability Allowed)\n")
                    md.write("| Question | Failures | Passes | Failure Rate |\n")
                    md.write("|----------|----------|--------|--------------|\n")

                    for question_key, data in sorted(additional_flaky.items()):
                        total = data["failures"] + data["passes"]
                        rate = (data["failures"] / total) * 100 if total else 0
                        display_question = data["question"] if data["question"] else question_key
                        if len(display_question) > MAX_QUESTION_DISPLAY_LENGTH:
                            display_question = display_question[: MAX_QUESTION_DISPLAY_LENGTH - 3] + "..."
                        md.write(f"| `{display_question}` | {data['failures']} | {data['passes']} | {rate:.0f}% |\n")

                    md.write("\n---\n\n#### 🔍 Additional Test Failure Details\n\n")

                    for question_key, data in sorted(additional_flaky.items()):
                        entry = data["last_fail"]
                        display_question = data["question"] if data["question"] else question_key
                        md.write(f"##### `{display_question}`\n\n")
                        md.write(f"**Failures:** {data['failures']} times\n\n")

                        if data["test_names"]:
                            test_names_str = ", ".join(f"`{tn}`" for tn in sorted(data["test_names"]))
                            md.write(f"**Test Names:** {test_names_str}\n\n")

                        if entry and entry.get("error_msg"):
                            log = entry["error_msg"].strip()
                            md.write("\n<details>\n")
                            md.write("<summary><strong>View full failure log</strong></summary>\n\n")
                            md.write("\n\n```\n")
                            md.write(log)
                            md.write("\n```\n")
                            md.write("</details>\n\n---\n\n")

                md.write("\n*Note: Connection failures (timeouts) are excluded from these statistics.*\n")

    print(f"Updated {REPORT_FILE}")


if __name__ == "__main__":
    main()
