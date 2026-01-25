# Backend setup guide

This guide walks you through setting up the **legislative** and **ArcGIS** ingestion pipelines. The default design is to run the legislative pipeline in **GitHub Actions**, but you can run everything locally or via cron if you prefer.

---

## 1) Prerequisites

- **Python 3.12+**
- A **Supabase project** (URL + service role key)
- Optional but recommended: a **Supabase database URL** for schema initialization
- GitHub repository access (for Actions-based runs)

---

## 2) Create the Supabase schema

This project ships with a SQL schema in `backend/schema.sql`.

### Option A: Initialize via script (recommended)

Set your database URL and run the initializer:

```bash
export DATABASE_URL="postgresql://<user>:<password>@<host>:<port>/<db>"
python -m backend.init_pipelines --pipeline legislative --action init
```

This applies `backend/schema.sql` and creates the tables.

### Option B: Run the SQL manually

Copy the contents of `backend/schema.sql` and run it inside your Supabase SQL editor.

---

## 3) Configure environment variables

Create a `.env` file (for local runs) or configure GitHub repository secrets (for Actions).

Minimum required for **legislative** ingestion:

```bash
SUPABASE_URL="https://<project>.supabase.co"
SUPABASE_SERVICE_ROLE_KEY="<service-role-key>"
```

Optional overrides for legislative data sources:

```bash
NJLEG_DOWNLOAD_BASE_URL="https://www.njleg.state.nj.us/downloads"
NJLEG_DOWNLOAD_TYPE="Bill_Tracking"
NJLEG_BILL_TRACKING_YEARS="2024"
NJLEG_VOTES_BASE_URL="https://pub.njleg.state.nj.us/votes"
NJLEG_VOTES_README_URL="https://pub.njleg.state.nj.us/votes/_Readme.txt"
NJLEG_VOTES_COMM_README_URL="https://pub.njleg.state.nj.us/votes/_CommRdme.txt"
NJLEG_GIS_SERVICE_URL="https://services2.arcgis.com/XVOqAjTOJ5P6ngMu/ArcGIS/rest/services/Legislative_Districts_of_NJ_Hosted_3424/FeatureServer/0"
NJLEG_LEGDB_README_URL="https://pub.njleg.state.nj.us/leg-databases/2024data/Readme.txt"
NJLEG_LEGDB_BASE_URL="https://pub.njleg.state.nj.us/leg-databases"
NJLEG_LEGDB_YEARS="2024,2022,2020"
DATA_RETENTION_DAYS="3"
BACKUP_RETENTION_COUNT="2"
BACKUP_INTERVAL_DAYS="14"
SESSION_LOOKBACK_COUNT="3"
SESSION_LENGTH_YEARS="2"
```

Additional required variables for **GIS** ingestion:

```bash
ARCGIS_REST_ROOT="https://services2.arcgis.com/<org-id>/ArcGIS/rest/services/"
ARCGIS_LEGISLATIVE_DISTRICTS_LAYER="Legislative_Districts_of_NJ_Hosted_3424/FeatureServer/0"
ARCGIS_QUERY_PAGE_SIZE="2000"
ARCGIS_TARGET_SRID="4326"
GIS_INGESTION_ENABLED="true"
```

---

## 4) Install dependencies

Legislative ingestion uses the Python standard library only:

```bash
pip install -r backend/requirements-legislative.txt
```

ArcGIS ingestion needs additional GIS + database libraries:

```bash
pip install -r backend/requirements-gis.txt
```

---

## 5) Manual initialization (recommended first run)

### Legislative pipeline

```bash
python -m backend.init_pipelines --pipeline legislative --action init
```

### ArcGIS pipeline

```bash
python -m backend.init_pipelines --pipeline gis --action init
```

Use `--skip-schema` if the schema is already created:

```bash
python -m backend.init_pipelines --pipeline gis --action init --skip-schema
```

---

## 6) Run the pipelines manually

### Legislative

```bash
python -m backend.init_pipelines --pipeline legislative --action run
```

### ArcGIS

```bash
python -m backend.init_pipelines --pipeline gis --action run
```

---

## 7) Default design: GitHub Actions (legislative ingestion)

The repository includes a workflow at `.github/workflows/legislative-ingestion.yml`.

### Step-by-step:

1. Go to **GitHub → Settings → Secrets and variables → Actions**.
2. Add the required secrets listed in the workflow (`SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, and the NJLEG_* values).
3. From the **Actions** tab, run **Legislative ingestion** manually once.
4. The workflow will then run on the schedule defined in the workflow file.

If you want to change the schedule, edit the cron expression in the workflow:

```yaml
schedule:
  - cron: "0 6 * * *"
```

---

## 8) Alternative to GitHub Actions (cron)

If you prefer a server-based cron job:

```bash
0 2 * * * /usr/bin/python /path/to/repo/backend/run_sync.py >> /var/log/njleg-sync.log 2>&1
```

---

## 9) Where to adjust ingestion settings

All ingestion settings are controlled via **environment variables**. This makes it easy to tune schedules or
source locations in GitHub Actions (secrets) or your server’s `.env` file.

For the legislature download scraper, the module is covered by unit tests in `backend/tests/test_legislative_downloads.py`,
which validates the download discovery logic.

---

## 10) Admin dashboard plan

See `backend/ADMIN_DASHBOARD.md` for the admin dashboard requirements, security model, and recommended tables to store
pipeline settings, logs, and user management metadata.
