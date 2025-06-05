"""Disaster Charter activations scraper
• Loops 2025→2000 through the JSON filter API
• Visits each legacy detail page (/web/guest/activations/-/article/<slug>)
• Extracts full table (type, location, timezone …)
• Writes CSV identical to the October-2024 format
"""

import csv
import os
import re
import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup

# ----------------------------------------------------------------------
# CONFIG
# ----------------------------------------------------------------------

BASE_API  = "https://disasterscharter.org/api-proxy/cos-api/api/public/library/activations"
BASE_SITE = "https://disasterscharter.org"
YEAR_FROM = 2000
YEAR_TO   = 2025          # inclusive
HEADERS   = {"User-Agent": "Mozilla/5.0"}
SLEEP_SEC = 0.35          # polite delay between page hits

OUT_DIR   = "./data_raw/disaster_charter/"
CSV_PATH  = os.path.join(OUT_DIR, "disaster_activations_web_scrape_2000_2025.csv")
os.makedirs(OUT_DIR, exist_ok=True)

# ----------------------------------------------------------------------
# LABEL MAPPING & DETAIL SCRAPER
# ----------------------------------------------------------------------

LABEL_PATTERNS = {
    "type_of_event"      : r"type of event",
    "location_of_event"  : r"location of event",
    "date_of_activation" : r"date of charter activation",
    "time_of_activation" : r"time of charter activation",
    "timezone"           : r"time zone of charter activation",
    "charter_requestor"  : r"charter requestor",
    "activation_id"      : r"activation id",
    "project_management" : r"project management",
    "value_adding"       : r"value adding",
}

def scrape_detail_page(slug: str) -> dict:
    """Slug e.g. 'flood-in-nigeria-activation-963-'
    Fetches /web/guest/activations/-/article/<slug>
    """
    url = f"{BASE_SITE}/web/guest/activations/-/article/{slug}"
    resp = requests.get(url, headers=HEADERS, timeout=25)
    if resp.status_code != 200:
        print("  ⚠️  detail page 404:", slug)
        return {k: "N/A" for k in LABEL_PATTERNS}

    soup = BeautifulSoup(resp.content, "html.parser")

    def pull(regex: str) -> str:
        pat = re.compile(regex + r":?$", re.IGNORECASE)
        lbl = soup.find(lambda tag: tag.string and pat.search(tag.string.strip()))
        if not lbl:
            return "N/A"
        val_cell = lbl.find_next("td") if lbl.name == "th" else lbl.find_next()
        return val_cell.get_text(strip=True) if val_cell else "N/A"

    return {k: pull(rgx) for k, rgx in LABEL_PATTERNS.items()}

# ----------------------------------------------------------------------
# MAIN COLLECTION LOOP
# ----------------------------------------------------------------------

def collect_rows():
    rows = []

    # ▶︎ reverse order: newest year first
    for yr in range(YEAR_TO, YEAR_FROM - 1, -1):
        print(f"• Year {yr}")
        params = {
            "from": f"{yr}-01-01 00:00:00",
            "to"  : f"{yr}-12-31 23:59:59",
        }
        try:
            data = requests.get(BASE_API, headers=HEADERS, params=params, timeout=25).json()
            acts = data.get("activations", [])
        except Exception as e:
            print("  ↳ API error:", e)
            continue

        for act in acts:
            slug = act.get("slug", "")
            if not slug:
                continue

            ts = act.get("dateAsTimestamp")
            if ts:
                dt  = datetime.utcfromtimestamp(ts / 1000)
                year, month = dt.year, dt.strftime("%B")
                date_str    = dt.strftime("%Y-%m-%d")
                pretty_date = dt.strftime("%d %A")          # ▶︎ 16 Wednesday
            else:
                year = month = date_str = pretty_date = "N/A"

            title     = act.get("title", "N/A")
            page_link = f"{BASE_SITE}/web/guest/activations/-/article/{slug}"

            details = scrape_detail_page(slug)
            time.sleep(SLEEP_SEC)

            rows.append([
                year, month, date_str, title, pretty_date, page_link,
                details["type_of_event"],
                details["location_of_event"],
                details["date_of_activation"],
                details["time_of_activation"],
                details["timezone"],
                details["charter_requestor"],
                details["activation_id"],
                details["project_management"],
                details["value_adding"],
            ])

    return rows

# ----------------------------------------------------------------------
# CSV WRITER
# ----------------------------------------------------------------------

def save_csv(rows):
    header = [
        "Year","Month","Date","Disaster","Formatted Date","Details Link",
        "Type of Event","Location of Event","Date of Activation","Time of Activation",
        "Timezone","Charter Requestor","Activation ID","Project Management","Value Adding",
    ]
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as fh:
        csv.writer(fh).writerows([header] + rows)
    print(f"✅  Saved {len(rows)} rows → {CSV_PATH}")

# ----------------------------------------------------------------------
# RUN
# ----------------------------------------------------------------------

if __name__ == "__main__":
    rows = collect_rows()
    if rows:
        save_csv(rows)
