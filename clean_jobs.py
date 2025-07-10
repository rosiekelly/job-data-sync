import json

# Load raw jobs from all-jobs.json (output of clean_scraped_jobs.py)
with open("all-jobs.json", "r") as f:
    jobs = json.load(f)

STANDARD_KEYS = {
    "title": ["role-title", "title", "job title", "name"],
    "location": ["role-location", "location", "job location"],
    "link": ["apply-button-href", "link", "url", "apply link"],
    "company": ["source", "company"],
    "description": ["role-description", "description", "job description", "role summary"],
    "status": ["role-status", "status", "job status", "availability", "status-text"]
}

def normalize(job):
    cleaned = {}

    # Map variant keys to standard keys
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

    # Only return if required fields exist
    return cleaned if "title" in cleaned and "link" in cleaned else None

# Deduplicate and filter jobs
seen = set()
cleaned_jobs = []

for job in jobs:
    norm = normalize(job)
    if norm and norm["status"] == "open":
        uid = (norm.get("title", ""), norm.get("link", ""))
        if uid not in seen:
            cleaned_jobs.append(norm)
            seen.add(uid)

# ✅ Save final cleaned version to all-jobs.json
with open("all-jobs.json", "w") as out:
    json.dump(cleaned_jobs, out, indent=2)

print(f"✅ Cleaned and normalized {len(cleaned_jobs)} job listings.")
