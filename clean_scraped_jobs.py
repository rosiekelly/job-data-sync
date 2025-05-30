import requests
import json
import os
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

# ============ CONFIG ============

API_KEY = os.environ["WS_API_KEY"]

SITEMAPS = {
    "1315385": "aldi-grads",
    "1315387": "BAE-systems",
    "1315388": "amazon-grads",
    "1315386": "AON-grads",
    "1315389": "arup-grads",
    "1315378": "Barclays-grads",
    "1315391": "capgemini-grads"
}

GSHEET_NAME = "Job Sync Output"

# Authenticate Google Sheets
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
client = gspread.authorize(creds)
sheet = client.open(GSHEET_NAME)

# ============ HELPER FUNCTION ============

def clean_job_data(raw_jobs, company_name):
    cleaned = []
    for job in raw_jobs:
        title = job.get("role-title", "").strip() or "No Title"
        location = job.get("role-location", job.get("posting-location", "")).strip() or "Unknown"
        job_url = job.get("apply-button-href", "").strip()
        salary = job.get("role-salary", "").strip() or "Undisclosed"
        status = job.get("role-status", "Open").strip() or "Open"

        cleaned.append({
            "title": title,
            "location": location,
            "url": job_url,
            "salary": salary,
            "company": company_name,
            "status": status
        })
    return cleaned

# ============ MAIN LOOP ============

all_cleaned = []

headers = {"Authorization": f"Token {API_KEY}"}

for sitemap_id, sheet_name in SITEMAPS.items():
    print(f"🛰️ Fetching sitemap: {sheet_name} ({sitemap_id})")

    # Get latest job ID for the sitemap
    jobs_url = f"https://api.webscraper.io/api/v1/sitemap/{sitemap_id}/jobs"
    jobs_resp = requests.get(jobs_url, headers=headers).json()

    if jobs_resp.get("jobs"):
        latest_job_id = jobs_resp["jobs"][0]["id"]
        print(f"✅ Latest job ID for {sheet_name}: {latest_job_id}")

        # Fetch scraped data
        data_url = f"https://api.webscraper.io/api/v1/job/{latest_job_id}/data"
        data_resp = requests.get(data_url, headers=headers)
        raw_jobs = data_resp.json().get("data", [])
    else:
        print(f"⚠️ No jobs found for sitemap: {sheet_name}")
        raw_jobs = []

    print(f"  ↳ Pulled {len(raw_jobs)} jobs")

    # Clean and prepare data
    cleaned_jobs = clean_job_data(raw_jobs, sheet_name.replace("-grads", "").upper())
    all_cleaned.extend(cleaned_jobs)

    # Write to individual tab
    print(f"📋 Cleaned jobs for {sheet_name}: {len(cleaned_jobs)}")
    if cleaned_jobs:
        df = pd.DataFrame(cleaned_jobs)
        try:
            worksheet = sheet.worksheet(sheet_name)
            worksheet.clear()
        except gspread.exceptions.WorksheetNotFound:
            worksheet = sheet.add_worksheet(title=sheet_name, rows="100", cols="10")
        worksheet.update([df.columns.values.tolist()] + df.values.tolist())
        print(f"✅ Uploaded {len(df)} jobs to tab: {sheet_name}")
    else:
        print(f"⚠️ No jobs to upload for {sheet_name}")

# Optionally write everything to local file (for debugging/logging)
with open("cleaned_jobs.json", "w", encoding="utf-8") as f:
    json.dump(all_cleaned, f, indent=2)

pd.DataFrame(all_cleaned).to_csv("cleaned_jobs.csv", index=False)
print(f"🎉 Done! Total jobs across all sitemaps: {len(all_cleaned)}")
