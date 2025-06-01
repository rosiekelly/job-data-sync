# ========== MAIN LOGIC ==========
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

    # Clean and upload
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
