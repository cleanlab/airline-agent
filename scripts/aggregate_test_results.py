import datetime
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

DATA_FILE = Path("stability_data.json")
REPORT_FILE = Path("README.md")

if not DATA_FILE.exists():
    print("No stability_data.json found — skipping report.")
    sys.exit(0)

today = datetime.datetime.now(datetime.UTC).date()
cutoff = today - datetime.timedelta(days=10)

# Load all entries
with open(DATA_FILE) as f:
    logs = json.load(f)

# Filter to last 10 days
recent = [
    x
    for x in logs
    if datetime.datetime.strptime(x["timestamp"], "%d-%m-%y %H:%M:%S").replace(tzinfo=datetime.UTC).date() >= cutoff
]

summary = defaultdict[Any, dict[str, int | set | None]](
    lambda: {"failures": 0, "passes": 0, "questions": set(), "last_fail": None}
)

for entry in recent:
    name = entry["test_name"]
    outcome = entry["outcome"]
    if outcome == "failed":
        summary[name]["failures"] += 1
        summary[name]["last_fail"] = entry
    elif outcome == "passed":
        summary[name]["passes"] += 1

    # Extract unique queries from stdout
    if entry.get("stdout"):
        matches = re.findall(r"^QUESTION:\s*(.+)$", entry["stdout"], flags=re.MULTILINE)
        for question_text in matches:
            summary[name]["questions"].add(question_text.strip())

# Generate Markdown
with open(REPORT_FILE, "w") as md:
    md.write(f"### 🧩 Stability Summary ({today})\n")
    md.write(f"*Aggregated from the last 10 days ({cutoff} → {today})*\n\n")

    flaky = {k: v for k, v in summary.items() if v["failures"] > 0}
    if not flaky:
        md.write("✅ All tests passed consistently in the last 10 days.\n")
        sys.exit(0)

    md.write("#### ❗ Flaky / Failing Tests\n")
    md.write("| Test | Failures | Passes | Failure Rate |\n")
    md.write("|------|-----------|--------|--------------|\n")

    for name, data in sorted(flaky.items()):
        total = data["failures"] + data["passes"]
        rate = (data["failures"] / total) * 100 if total else 0
        md.write(f"| `{name}` | {data['failures']} | {data['passes']} | {rate:.0f}% |\n")

    md.write("\n---\n\n#### 🔍 Failure Details\n\n")

    for name, data in sorted(flaky.items()):
        entry = data["last_fail"]
        md.write(f"##### `{name}`\n")
        md.write(f"**Failures:** {data['failures']} times\n")
        if data["questions"]:
            md.write("**Questions observed:**\n")
            for q in sorted(data["questions"]):
                md.write(f"- {q}\n")
        if entry and entry.get("stderr"):
            log = entry["stderr"].strip()
            md.write("\n<details>\n")
            md.write("<summary><strong>View full failure log</strong></summary>\n\n")
            md.write("\n\n```\n")
            md.write(log)
            md.write("\n```\n")
            md.write("</details>\n\n---\n\n")

print(f"Updated {REPORT_FILE}")
