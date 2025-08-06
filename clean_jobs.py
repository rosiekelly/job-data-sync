import json
import os

# Load all scraped jobs
with open("all-jobs.json", "r", encoding="utf-8") as f:
    all_jobs = json.load(f)

cleaned_jobs = []
skipped_jobs = []

TITLE_FIELDS = ["role-title", "role-name", "title", "name"]
PROGRAMME_LINK_FIELDS = [
    "programme-page", "programme-link", "programme-list",
    "programme-page-href", "role-page", "role-page-href", "job-page-href"
]
APPLY_LINK_FIELDS = [
    "apply-link", "apply-link-href", "apply-button", "apply-button-href"
]
LOCATION_FIELDS = ["location", "office-location", "job-location", "city"]
DESCRIPTION_FIELDS = ["description", "job-description", "role-description"]

def get_first_existing_field(job, fields):
    for field in fields:
        if field in job and job[field] and str(job[field]).strip():
            return job[field]
    return None

def is_url(val):
    return isinstance(val, str) and (
        val.startswith("http://") or val.startswith("https://")
    )

def infer_company_from_source(source):
    if not source:
        return None
    name = source.replace("-grads", "")\
                 .replace("-graduates", "")\
                 .replace("-jobs", "")\
                 .replace("-", " ")\
                 .strip()
    return name.title()

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

    # Determine link
    link = None

    if job.get("source") == "brightnetwork-grads":
        # For Bright Network jobs, try apply-button-href first
        button_href = job.get("apply-button-href")
        if is_url(button_href):
            link = button_href.strip()
        else:
            # Fall back to original apply/programme logic
            for field in APPLY_LINK_FIELDS + PROGRAMME_LINK_FIELDS:
                val = job.get(field)
                if is_url(val):
                    link = val.strip()
                    break
    else:
        # For all other jobs, use original programme-first logic
        for field in PROGRAMME_LINK_FIELDS:
            val = job.get(field)
            if is_url(val):
                link = val.strip()
                break
        if not link:
            for field in APPLY_LINK_FIELDS:
                val = job.get(field)
                if is_url(val):
                    link = val.strip()
                    break

    # Validate link
    if not is_url(link):
        skipped_jobs.append({
            "title": title,
            "reason": "missing valid link",
            "raw": raw
        })
        continue

    # Extract location and description if available
    location = get_first_existing_field(job, LOCATION_FIELDS)
    description = get_first_existing_field(job, DESCRIPTION_FIELDS)

    cleaned["title"] = title.strip()
    cleaned["link"] = link
    if location:
        cleaned["location"] = location.strip()
    if description:
        cleaned["description"] = description.strip()

    # Company handling
    if job.get("source") == "brightnetwork-grads":
        cleaned["source"] = job["source"]
        cleaned["company"] = job.get("company-name") if job.get("company-name") else None
    else:
        if "source" in job:
            cleaned["source"] = job["source"]
            cleaned["company"] = infer_company_from_source(job["source"])
        else:
            cleaned["company"] = None

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
    print("🟡 Skipped preview:")
    for j in skipped_jobs[:5]:
        print(f"• Reason: {j['reason']} | Title: {j['title']}")
