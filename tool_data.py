def fetch_and_summarize_data(source):
    # Connect to a DB or use a mockup for demo
    data = [
        {"date": "2025-08-19", "sales": 1200},
        {"date": "2025-08-20", "sales": 1450}
    ]
    total = sum(row["sales"] for row in data)
    summary = f"Total sales: {total} (from {len(data)} days)"
    return {"summary": summary, "raw": data}
