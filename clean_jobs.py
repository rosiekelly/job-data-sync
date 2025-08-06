for job in all_jobs:
    cleaned = {}
    raw = job.copy()

    # Extract title
    title = get_first_existing_field(job, TITLE_FIELDS)
    if not title:
        skipped_jobs.append({
            "title": None,
            "reason": "missing title",
            "raw": raw
        })
        continue

    # Determine link depending on source
    source = job.get("source", "")
    link = None
    if "brightnetwork-grads" in source:
        # For brightnetwork-grads, use only "apply-button-href"
        val = job.get("apply-button-href")
        if is_url(val):
            link = val.strip()
    else:
        # For all other sources, use original logic
        for field in PROGRAMME_LINK_FIELDS:
            val = job.get(field)
            if is_url(val):
                link = val.strip()
                break
        if not link:
            button_val = job.get("apply-button")
            button_href = job.get("apply-button-href")
            if is_url(button_href):
                link = button_href.strip()
            elif is_url(button_val):
                link = button_val.strip()
            else:
                for field in APPLY_LINK_FIELDS:
                    val = job.get(field)
                    if is_url(val):
                        link = val.strip()
                        break

    # Validate link
    if not is_url(link):
        skipped_jobs.append({
            "title": title,
            "reason": "missing valid link",
            "raw": raw
        })
        continue

    # Extract location and description if available
    location = get_first_existing_field(job, LOCATION_FIELDS)
    description = get_first_existing_field(job, DESCRIPTION_FIELDS)

    cleaned["title"] = title.strip()
    cleaned["link"] = link
    if location:
        cleaned["location"] = location.strip()
    if description:
        cleaned["description"] = description.strip()
    if "source" in job:
        cleaned["source"] = job["source"]
        cleaned["company"] = infer_company_from_source(job["source"])
    else:
        cleaned["company"] = None

    cleaned_jobs.append(cleaned)
