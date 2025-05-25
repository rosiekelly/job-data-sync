import requests
import json

# CONFIG
import os
API_KEY = os.environ["WS_API_KEY"]
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
# Convert JSON to DataFrame and save as CSV
import pandas as pd

df = pd.DataFrame(cleaned_jobs)

# Optional: Clean column names if needed
df.columns = [col.lower().strip().replace(" ", "_") for col in df.columns]

# Save as CSV
df.to_csv("cleaned_jobs.csv", index=False)
print(f"✅ Also saved cleaned jobs to cleaned_jobs.csv")
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

# Step 1: Authenticate to Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = json.loads(open("creds.json").read())  # creds.json will be created by GitHub Action
credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds, scope)
client = gspread.authorize(credentials)

# Step 2: Open your spreadsheet and upload the cleaned data
sheet = client.open("Job Sync Output").sheet1
sheet.clear()  # remove old rows
sheet.update([df.columns.tolist()] + df.values.tolist())  # upload the new data

print("✅ Cleaned jobs uploaded to Google Sheets")

