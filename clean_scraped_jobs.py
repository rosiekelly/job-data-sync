import requests
import json
import os
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

# ========== CONFIG ==========
raw_key = os.environ["WS_API_KEY"]
API_KEY = raw_key.strip()

print(f"🔐 Web Scraper API Key length: {len(API_KEY)}")
print(f"🔐 Web Scraper API Key preview: {API_KEY[:5]}...")

# Add your Web Scraper Sitemap IDs and sheet tab names
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


# ============ Google Sheets Auth ============
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
client = gspread.authorize(creds)
sheet = client.open(GSHEET_NAME)

# ============ Helper Function ============
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

# ============ Main Loop ============
all_cleaned = []
headers = {"Authorization": f"Token {API_KEY}"}

for sitemap_id, sheet_name in SITEMAPS.items():
    print(f"📡 Fetching latest job for {sheet_name} (Sitemap ID: {sitemap_id})")

    # Get latest job ID
    jobs_url = f"https://api.webscraper.io/api/v1/sitemap/{sitemap_id}/jobs"
    jobs_resp = requests.get(jobs_url, headers=headers).json()

    if not jobs_resp.get("jobs"):
        print(f"⚠️ No jobs found for {sheet_name}")
        continue

    latest_job_id = jobs_resp["jobs"][0]["id"]
    print(f"✅ Latest job ID: {latest_job_id}")

    # Get job data
    data_url = f"https://api.webscraper.io/api/v1/job/{latest_job_id}/data"
    data_resp = requests.get(data_url, headers=headers).json()
    raw_jobs = data_resp.get("data", [])
    print(f"📥 Pulled {len(raw_jobs)} jobs")

    # Clean and collect
    cleaned_jobs = clean_job_data(raw_jobs, sheet_name.replace("-grads", "").upper())
    all_cleaned.extend(cleaned_jobs)

    # Write to Google Sheet tab
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

# Optionally write to local file
with open("cleaned_jobs.json", "w", encoding="utf-8") as f:
    json.dump(all_cleaned, f, indent=2)
pd.DataFrame(all_cleaned).to_csv("cleaned_jobs.csv", index=False)
print(f"🎉 Done! Total jobs across all sitemaps: {len(all_cleaned)}")
