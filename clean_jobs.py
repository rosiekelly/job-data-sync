import json
from datetime import datetime
from pathlib import Path

INPUT_FILE = "all-jobs.json"
OUTPUT_FILE = "cleaned_jobs.json"
SKIPPED_FILE = "skipped_jobs.json"

# Priority order for extracting fields
TITLE_FIELDS = ["role-title", "title", "name"]
LINK_FIELDS = ["programme-link-href", "programme-page-href", "apply-button-href", "apply-link"]

def get_first_nonempty_field(job, fields):
    for field in fields:
        val = job.get(field)
        if val and isinstance(val, str) and val.strip():
            return val.strip()
    return ""

def clean_job(job):
    title = get_first_nonempty_field(job, TITLE_FIELDS)
    link = get_first_nonempty_field(job, LINK_FIELDS)

    if not title or not link:
        reason_parts = []
        if not title:
            reason_parts.append("missing title")
        if not link:
            reason_parts.append("missing link")
        return None, " | ".join(reason_parts)

    return {
        "title": title,
        "link": link,
        "description": job.get("description", "").strip(),
        "location": job.get("Location", "").strip(),
        "salary": job.get("salary", "").strip(),
        "duration": job.get("duration", "").strip(),
        "status": job.get("status-text", "").strip(),
        "source": job.get("source", "").strip(),
        "scraped-from": job.get("web-scraper-start-url", "").strip(),
        "scraped-at": datetime.utcnow().isoformat() + "Z"
    }, None

def main():
    with open(INPUT_FILE, "r") as f:
        raw_jobs = json.load(f)

    cleaned_jobs = []
    skipped_jobs = []

    for job in raw_jobs:
        cleaned, reason = clean_job(job)
        if cleaned:
            cleaned_jobs.append(cleaned)
        else:
            skipped_jobs.append({
                "title": job.get("title") or job.get("name"),
                "reason": reason,
                "raw": job
            })

    with open(OUTPUT_FILE, "w") as f:
        json.dump(cleaned_jobs, f, indent=2)

    if skipped_jobs:
        with open(SKIPPED_FILE, "w") as f:
            json.dump(skipped_jobs, f, indent=2)

        print(f"⚠️ Skipped {len(skipped_jobs)} jobs. See {SKIPPED_FILE} for details.")
        print("⚠️ Skipped jobs preview:")
        for job in skipped_jobs[:5]:
            print(f"  - Reason: {job['reason']} | Title: {job.get('title')}")
    else:
        print("✅ No skipped jobs.")

    print(f"✅ Cleaned and normalized {len(cleaned_jobs)} job listings.")

if __name__ == "__main__":
    main()
