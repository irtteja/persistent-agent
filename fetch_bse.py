#!/usr/bin/env python3
"""BSE announcement monitor — run once per relay generation."""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


PAGE_SIZE = 50  # BSE default results per page


def fetch_new_announcements(b, last_seen: set) -> tuple[list, list]:
    """
    Fetch announcements page by page until we hit a known NEWSID or run out.
    Returns (new_announcements, all_ids_from_page1).
    Raises on any fetch failure so caller can abort without updating state.
    """
    new_anns = []
    page1_ids = []

    page = 1
    while True:
        data = b.announcements(page_no=page)
        rows = data.get("Table", [])

        if not rows:
            break

        if page == 1:
            page1_ids = [r["NEWSID"] for r in rows]

        found_known = False
        for row in rows:
            if row["NEWSID"] in last_seen:
                found_known = True
                break
            new_anns.append(row)

        # Stop if we hit a known ID, or fewer results than a full page (last page)
        if found_known or len(rows) < PAGE_SIZE:
            break

        page += 1

    return new_anns, page1_ids


def main():
    from bse import BSE

    repo_dir = Path(__file__).resolve().parent
    state_file = repo_dir / "state.json"
    log_file = repo_dir / "announcements.log"

    with open(state_file) as f:
        state = json.load(f)

    last_seen = set(state.get("last_seen_newsids", []))

    b = BSE(download_folder="/tmp/bse-monitor")

    # Fetch — let exceptions propagate so the caller knows not to update state
    new_anns, page1_ids = fetch_new_announcements(b, last_seen)

    print(f"Found {len(new_anns)} new announcement(s)")

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

    # Only update last_seen_newsids if we successfully fetched page 1
    # (page1_ids is always the freshest window; known IDs beyond it are stale)
    if page1_ids:
        # Keep all new IDs we found + the full page-1 window
        all_seen = {a["NEWSID"] for a in new_anns} | set(page1_ids)
        state["last_seen_newsids"] = list(all_seen)
        state["last_check"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        with open(state_file, "w") as f:
            json.dump(state, f, indent=2)

    return len(new_anns)


if __name__ == "__main__":
    try:
        count = main()
        sys.exit(0)
    except Exception as e:
        # Print error but exit non-zero so the agent knows not to commit state
        print(f"FETCH FAILED: {e}", file=sys.stderr)
        sys.exit(1)
