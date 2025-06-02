import json
import csv

with open("all-jobs.json", "r") as f:
    jobs = json.load(f)

STANDARD_KEYS = {
    "title": ["job title", "title", "role"],
    "location": ["location", "job location"],
    "link": ["link", "url", "job url", "apply link"],
    "company": ["company", "source"],
    "description": ["description", "job description", "role summary"],
    "status": ["status", "job status", "availability"]
}

def normalize(job):
    cleaned = {}
    for std_key, variants in STANDARD_KEYS.items():
        for key in job:
            if key.strip().lower() in variants:
                cleaned[std_key] = job[key].strip()
                break

    # Handle status logic
    raw_status = cleaned.get("status", "").lower()
    if "closed" in raw_status:
        cleaned["status"] = "closed"
    elif "opening" in raw_status:
        cleaned["status"] = "closed"
    elif "status" not in cleaned:
        cleaned["status"] = "open"
    else:
        cleaned["status"] = "open"

    return cleaned if "title" in cleaned and "link" in cleaned else None

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

print(f"✅ Cleaned and normalized {len(cleaned_jobs)} job listings.")
