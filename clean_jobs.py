import json
import csv

# Load raw job data
with open("all-jobs.json", "r") as f:
    jobs = json.load(f)

# Define standard keys and their variants
STANDARD_KEYS = {
    "title": ["job title", "title", "role", "role-title"],
    "location": ["location", "job location", "role-location"],
    "link": ["link", "url", "job url", "apply link", "apply-button-href"],
    "company": ["company", "source"],
    "description": ["description", "job description", "role summary", "role-description"],
    "status": ["status", "job status", "availability", "role-status", "status-text"]
}

# Normalise a single job entry
def normalize(job):
    cleaned = {}

    # Match job keys to standard ones
    for std_key, variants in STANDARD_KEYS.items():
        for key in job:
            for variant in variants:
                if key.strip().lower() == variant.strip().lower():
                    cleaned[std_key] = str(job[key]).strip()
                    break

    # Handle job status
    raw_status = cleaned.get("status", "").lower()
    if "closed" in raw_status:
        cleaned["status"] = "closed"
    elif "opening" in raw_status:
        cleaned["status"] = "closed"
    elif "status" not in cleaned:
        cleaned["status"] = "open"
    else:
        cleaned["status"] = "open"

    # Only include if has both title and link
    return cleaned if "title" in cleaned and "link" in cleaned else None

# Deduplicate & clean all jobs
seen = set()
cleaned_jobs = []

for job in jobs:
    norm = normalize(job)
    if norm:
        uid = (norm.get("title", ""), norm.get("link", ""))
        if uid not in seen:
            cleaned_jobs.append(norm)
            seen.add(uid)

# Save to JSON
with open("cleaned-jobs.json", "w") as out:
    json.dump(cleaned_jobs, out, indent=2)

# Save to CSV
with open("cleaned-jobs.csv", "w", newline='') as out_csv:
    writer = csv.DictWriter(out_csv, fieldnames=["title", "location", "company", "link", "description", "status"])
    writer.writeheader()
    writer.writerows(cleaned_jobs)

# Log result
print(f"✅ Cleaned and normalized {len(cleaned_jobs)} job listings.")
