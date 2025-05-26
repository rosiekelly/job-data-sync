import requests
import json
import os
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

# ============== CONFIG ==============
API_KEY = os.environ["WS_API_KEY"]

# Add your Web Scraper JOB IDs (not sitemap IDs!) and the corresponding tab names:
SITEMAPS = {
    "30912566": "aldi-grads",
    "30912567": "amazon-grads",
    "30912574": "BAE-systems",
    "30804873": "Barclays-grads",
    "30886695": "capgemini-grads",
    "30886692": "DEUTSCHE-BANK-GRADS",
    "30886694": "deloitte-grads"
}

GSHEET_NAME = "Job Sync Output"  # Make sure this matches your actual Google Sheet title


# Authenticate Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
client = gspread.authorize(creds)
sheet = client.open(GSHEET_NAME)

# ----------------- HELPER FUNCTION -------------------
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

# ----------------- MAIN LOOP -------------------
all_cleaned = []

for sitemap_id, sheet_name in SITEMAPS.items():
    print(f"📡 Fetching sitemap: {sheet_name} ({sitemap_id})")
    url = f"https://api.webscraper.io/api/v1/sitemap/{sitemap_id}/data"
    headers = {"Authorization": f"Token {API_KEY}"}
    response = requests.get(url, headers=headers)
    raw_jobs = response.json().get("data", [])
    print(f"   ↳ Pulled {len(raw_jobs)} jobs")

    cleaned_jobs = clean_job_data(raw_jobs, sheet_name.replace("-grads", "").upper())
    all_cleaned.extend(cleaned_jobs)

    # Write to individual tab
    print(f"🔍 Cleaned jobs for {sheet_name}: {cleaned_jobs}")
    if cleaned_jobs:
        df = pd.DataFrame(cleaned_jobs)
        try:
            worksheet = sheet.worksheet(sheet_name)
            worksheet.clear()
        except gspread.exceptions.WorksheetNotFound:
            worksheet = sheet.add_worksheet(title=sheet_name, rows="100", cols="10")
        worksheet.update([df.columns.values.tolist()] + df.values.tolist())
        print(f"   ✅ Uploaded {len(df)} jobs to tab: {sheet_name}")
    else:
        print(f"   ⚠️ No jobs to upload for {sheet_name}")

# Optionally write everything to local file
with open("cleaned_jobs.json", "w", encoding="utf-8") as f:
    json.dump(all_cleaned, f, indent=2)
pd.DataFrame(all_cleaned).to_csv("cleaned_jobs.csv", index=False)
print(f"📁 Done! Total jobs across all sitemaps: {len(all_cleaned)}")
