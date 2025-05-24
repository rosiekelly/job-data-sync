import requests
import json

# CONFIG
API_KEY = "YOUR_API_KEY_HERE"
SITEMAP_ID = "YOUR_SITEMAP_ID_HERE"

headers = {"Authorization": f"Token {API_KEY}"}
url = f"https://api.webscraper.io/api/v1/sitemap/{SITEMAP_ID}/data"

response = requests.get(url, headers=headers)
raw_jobs = response.json().get('data', [])

cleaned_jobs = []

for job in raw_jobs:
    title = job.get('job_title', '').strip() or 'No Title'
    location = job.get('job_location', '').strip() or 'Unknown'
    job_url = job.get('apply_link', '').strip()
    salary = job.get('salary', '').strip() or 'Undisclosed'

    # Company name from URL
    if "ey.com" in job_url:
        company = "EY"
    elif "amazon.jobs" in job_url:
        company = "Amazon"
    elif "brightnetwork" in job_url:
        company = "Bright Network"
    else:
        company = "Unknown"

    # Status logic
    status_text = job.get('status', '').strip().lower()
    closed_indicators = ["closed", "applications closed", "roles opening", "opens", "opening in", "applications open in"]
    status = "Closed" if any(phrase in status_text for phrase in closed_indicators) else "Open"

    cleaned_jobs.append({
        "title": title,
        "location": location,
        "url": job_url,
        "salary": salary,
        "company": company,
        "status": status
    })

with open("cleaned_jobs.json", "w", encoding="utf-8") as f:
    json.dump(cleaned_jobs, f, indent=2)

print(f"✅ Cleaned and saved {len(cleaned_jobs)} jobs to cleaned_jobs.json")
