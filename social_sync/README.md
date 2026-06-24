# Social Sync

API-driven social media data pipeline for the Power BI Social Media Performance Dashboard.

## What It Does

- Pulls Facebook and Instagram metrics from the Meta Graph API.
- Stores profile, post, reach, engagement, and media data in SQL tables.
- Supports scheduled refresh jobs for ongoing dashboard updates.
- Feeds the published Power BI dashboard through a database/Fabric Gateway workflow.

## Stack

- Python
- FastAPI
- Meta Graph API
- SQL database
- Power BI
- Fabric Gateway

## Setup

1. Copy `.env.example` to `.env`.
2. Fill in database, Meta account, and token values.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run the API:

```bash
uvicorn App:app --reload
```

The real `.env` file is intentionally not committed.
