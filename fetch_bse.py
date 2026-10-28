#!/usr/bin/env python3
"""BSE announcement monitor — run once per relay generation."""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def main():
    from bse import BSE

    repo_dir = Path(__file__).resolve().parent
    state_file = repo_dir / "state.json"
    log_file = repo_dir / "announcements.log"

    with open(state_file) as f:
        state = json.load(f)

    last_seen = set(state.get("last_seen_newsids", []))

    b = BSE(download_folder="/tmp/bse-monitor")
    data = b.announcements(page_no=1)
    announcements = data.get("Table", [])

    if not announcements:
        print("No announcements returned")
        return 0

    new_anns = [a for a in announcements if a["NEWSID"] not in last_seen]
    print(f"Fetched {len(announcements)} announcements, {len(new_anns)} new")

    if new_anns:
        with open(log_file, "a") as f:
            for ann in new_anns:
                line = (
                    f"{ann['DT_TM']} | "
                    f"{ann.get('SCRIP_CD', '')} | "
                    f"{ann.get('SLONGNAME', '').strip()} | "
                    f"{ann.get('HEADLINE', '').strip()}\n"
                )
                f.write(line)
                print(f"  NEW: {line.strip()}")

    state["last_seen_newsids"] = [a["NEWSID"] for a in announcements]
    state["last_check"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    with open(state_file, "w") as f:
        json.dump(state, f, indent=2)

    return len(new_anns)


if __name__ == "__main__":
    count = main()
    sys.exit(0)
