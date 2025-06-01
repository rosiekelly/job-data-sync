import requests
import json
import os
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

# ========== CONFIG ==========
API_KEY = os.environ["WS_API_KEY"]

# Sitemap ID : Sheet Tab Name
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

# ========== AUTHENTICATE GOOGLE SHEETS ==========
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
client = gspread.authorize(creds)
sheet = client.open(GSHEET_NAME)

# ========== HELPER FUNCTION ==========
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

# ========== MAIN LOOP ==========
all_cleaned = []
headers = {"Authorization": f"Token {API_KEY}"}

for sitemap_id, sheet_name in SITEMAPS.items():
    print(f"\n🔍 Fetching latest job for {sheet_name} (Sitemap ID: {sitemap_id})")

    jobs_url = f"https://api.webscraper.io/api/v1/sitemap/{sitemap_id}/jobs"
    jobs_resp = requests.get(jobs_url, headers=headers).json()

    raw_jobs = []
    if jobs_resp.get("jobs"):
        for job in jobs_resp["jobs"]:
            job_id = job["id"]
            data_url = f"https://api.webscraper.io/api/v1/job/{job_id}/data"
            data_resp = requests.get(data_url, headers=headers).json()
            data = data_resp.get("data", [])
            if data:
                raw_jobs = data
                print(f"✅ Found job ID: {job_id} with {len(data)} records")
                break
        else:
            print(f"⚠️ No jobs with records found for {sheet_name}")
    else:
        print(f"⚠️ No jobs found at all for {sheet_name}")

    cleaned_jobs = clean_job_data(raw_jobs, sheet_name.replace("-grads", "").upper())
    all_cleaned.extend(cleaned_jobs)

    print(f"🧹 Cleaned jobs for {sheet_name}: {len(cleaned_jobs)}")
    if cleaned_jobs:
        df = pd.DataFrame(cleaned_jobs)
        try:
            worksheet = sheet.worksheet(sheet_name)
            worksheet.clear()
        except gspread.exceptions.WorksheetNotFound:
            worksheet = sheet.add_worksheet(title=sheet_name, rows="100", cols="10")
        worksheet.update([df.columns.values.tolist()] + df.values.tolist())
        print(f"📤 Uploaded {len(df)} jobs to: {sheet_name}")
    else:
        print(f"⚠️ No jobs to upload for {sheet_name}")

# Optionally write everything to local files
with open("cleaned_jobs.json", "w", encoding="utf-8") as f:
    json.dump(all_cleaned, f, indent=2)

pd.DataFrame(all_cleaned).to_csv("cleaned_jobs.csv", index=False)
print(f"\n✅ Done! Total jobs across all sitemaps: {len(all_cleaned)}")
