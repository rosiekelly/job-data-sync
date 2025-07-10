import json

# Load all scraped jobs
with open("all-jobs.json") as f:
    all_jobs = json.load(f)

cleaned_jobs = []
skipped_jobs = []
seen = set()

for job in all_jobs:
    title = (
        job.get("role-title")
        or job.get("title")
        or job.get("name")
        or ""
    ).strip()

    link = (
        job.get("apply-button-href")
        or job.get("programme-page-href")
        or job.get("programme-link-href")
        or job.get("apply-link")
        or ""
    ).strip()

    if not title or not link:
        reason = []
        if not title:
            reason.append("missing title")
        if not link:
            reason.append("missing link")

        skipped_jobs.append({
            "reason": ", ".join(reason),
            "job_data": job
        })
        continue

    location = (
        job.get("role-location")
        or job.get("Location")
        or job.get("location")
        or "Unknown"
    ).strip()

    salary = (
        job.get("role-salary")
        or job.get("salary")
        or "Undisclosed"
    ).strip()

    status = (
        job.get("role-status")
        or job.get("status-text")
        or job.get("status")
        or "Open"
    ).strip()

    company = job.get("source", "Unknown")

    cleaned = {
        "title": title,
        "location": location,
        "url": link,
        "salary": salary,
        "company": company,
        "status": status
    }

    uid = (title, link)
    if uid not in seen:
        cleaned_jobs.append(cleaned)
        seen.add(uid)

# Save cleaned and skipped jobs
with open("cleaned_jobs.json", "w") as f:
    json.dump(cleaned_jobs, f, indent=2)

with open("skipped_jobs.json", "w") as f:
    json.dump(skipped_jobs, f, indent=2)

print(f"✅ Cleaned and normalized {len(cleaned_jobs)} job listings.")
print(f"⚠️ Skipped {len(skipped_jobs)} jobs. See skipped_jobs.json for details.")

# Optionally print a few skipped job summaries
if skipped_jobs:
    print("\n⚠️ Skipped jobs preview:")
    for job in skipped_jobs[:5]:
        raw = job["job_data"]
        title_preview = raw.get("role-title") or raw.get("title") or raw.get("name") or "No title"
        print(f"- Reason: {job['reason']} | Title: {title_preview}")
