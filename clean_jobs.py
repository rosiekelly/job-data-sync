import json
import os

# Load all scraped jobs
with open("all-jobs.json", "r", encoding="utf-8") as f:
    all_jobs = json.load(f)

cleaned_jobs = []
skipped_jobs = []

# Priority fields for extracting data
TITLE_FIELDS = ["role-title", "role-name", "title", "name"]
LINK_FIELDS = [
    "link",
    "apply-button-href",
    "apply_link",
    "url",
    "programme-link-href"  # <-- newly added
]
LOCATION_FIELDS = ["location", "office-location", "job-location", "city"]
DESCRIPTION_FIELDS = ["description", "job-description", "role-description"]

def get_first_existing_field(job, fields):
    for field in fields:
        if field in job and job[field] and str(job[field]).strip():
            return job[field]
    return None

for job in all_jobs:
    cleaned = {}
    raw = job.copy()

    # Extract title
    title = get_first_existing_field(job, TITLE_FIELDS)
    if not title:
        skipped_jobs.append({
            "title": None,
            "reason": "missing title",
            "raw": raw
        })
        continue

    # Extract link
    link = get_first_existing_field(job, LINK_FIELDS)
    if not link:
        skipped_jobs.append({
            "title": title,
            "reason": "missing link",
            "raw": raw
        })
        continue

    # Extract location and description if available
    location = get_first_existing_field(job, LOCATION_FIELDS)
    description = get_first_existing_field(job, DESCRIPTION_FIELDS)

    cleaned["title"] = title.strip()
    cleaned["link"] = link.strip()
    if location:
        cleaned["location"] = location.strip()
    if description:
        cleaned["description"] = description.strip()
    if "source" in job:
        cleaned["source"] = job["source"]

    cleaned_jobs.append(cleaned)

# Write cleaned jobs to file
with open("cleaned_jobs.json", "w", encoding="utf-8") as f:
    json.dump(cleaned_jobs, f, ensure_ascii=False, indent=2)

# Write skipped jobs to file
if skipped_jobs:
    with open("skipped_jobs.json", "w", encoding="utf-8") as f:
        json.dump(skipped_jobs, f, ensure_ascii=False, indent=2)

# Output summary
print(f"✅ Cleaned and normalized {len(cleaned_jobs)} job listings.")
if skipped_jobs:
    print(f"⚠️ Skipped {len(skipped_jobs)} jobs. See skipped_jobs.json for details.")
    print("🔶 Skipped jobs preview:")
    for j in skipped_jobs[:5]:
        print(f" - Reason: {j['reason']} | Title: {j['title']}")
    print("🔸 Some jobs were skipped. See skipped_jobs.json")
