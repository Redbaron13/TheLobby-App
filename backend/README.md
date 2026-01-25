# NJ Legislature Data Pipeline

This backend module downloads NJ Legislature data files, cleans them, and upserts changes into Supabase. It is designed to run daily (via GitHub Actions by default, or cron/server jobs) and only pushes changed rows while keeping a small rolling history and periodic backups. For step-by-step setup, see `backend/SETUP.md`.

## Data Sources
- `https://www.njleg.state.nj.us/downloads`

The pipeline currently targets:
- `MAINBILL.TXT` (bills)
- `ROSTER.TXT` (legislators)
- `BILLSPON.TXT` (bill sponsors)
- `COMEMBER.TXT` (committee memberships)
- Vote files discovered from `_Readme.txt` and `_CommRdme.txt` under `https://pub.njleg.state.nj.us/votes`
- NJ legislative district GIS data from ArcGIS (feature layer)

## Environment Variables

```bash
export NJLEG_DOWNLOAD_BASE_URL="https://www.njleg.state.nj.us/downloads"
export NJLEG_DOWNLOAD_TYPE="Bill_Tracking"
export NJLEG_BILL_TRACKING_YEARS="2024"
export NJLEG_VOTES_BASE_URL="https://pub.njleg.state.nj.us/votes"
export NJLEG_VOTES_README_URL="https://pub.njleg.state.nj.us/votes/_Readme.txt"
export NJLEG_VOTES_COMM_README_URL="https://pub.njleg.state.nj.us/votes/_CommRdme.txt"
export NJLEG_GIS_SERVICE_URL="https://services2.arcgis.com/XVOqAjTOJ5P6ngMu/ArcGIS/rest/services/Legislative_Districts_of_NJ_Hosted_3424/FeatureServer/0"
export NJLEG_LEGDB_README_URL="https://pub.njleg.state.nj.us/leg-databases/2024data/Readme.txt"
export NJLEG_LEGDB_BASE_URL="https://pub.njleg.state.nj.us/leg-databases"
export NJLEG_LEGDB_YEARS="2024,2022,2020"
export SUPABASE_URL="https://zgtevahaudnjpocptzgj.supabase.co"
export SUPABASE_SERVICE_ROLE_KEY="<service-role-key>"
export SUPABASE_ANON_KEY="<anon-key>"
export DATA_RETENTION_DAYS=3
export BACKUP_RETENTION_COUNT=2
export BACKUP_INTERVAL_DAYS=14
export SESSION_LOOKBACK_COUNT=3
export SESSION_LENGTH_YEARS=2
```

## Run a Manual Sync

```bash
python backend/run_sync.py
```

You can also use the unified initializer/runner:

```bash
python -m backend.init_pipelines --pipeline legislative --action run
```

You can set a specific date if you are backfilling data:

```bash
python backend/run_sync.py --date 2025-03-15
```

## Scheduling (Cron)

Run nightly at 2 AM:

```bash
0 2 * * * /usr/bin/python /path/to/repo/backend/run_sync.py >> /var/log/njleg-sync.log 2>&1
```

## GitHub Actions (Default)

The default design is to run ingestion from GitHub Actions. See `.github/workflows/legislative-ingestion.yml`
and `backend/SETUP.md` for the exact steps to configure repository secrets and schedule.

## Supabase Tables

Use `backend/schema.sql` to create the tables and indexes in Supabase before running the sync.

## Requirements files

The ingestion pipelines have explicit requirements files:

- `backend/requirements-legislative.txt` (stdlib-only for legislative ingestion)
- `backend/requirements-gis.txt` (ArcGIS + PostGIS dependencies)

## Notes
- The pipeline stores raw downloads in `backend/data/raw/<YYYY-MM-DD>/` and processed snapshots in `backend/data/processed/<YYYY-MM-DD>/`.
- Only changed rows are upserted to Supabase by comparing row hashes against the previous snapshot.
- Backups capture full datasets on a schedule and are retained separately to guard against data corruption.
- Vote files are stored in `backend/data/raw/<YYYY-MM-DD>/votes/` and parsed into a `vote_records` table with raw payloads for forward-compatible schema updates.
- GIS district polygons are stored as GeoJSON in the `districts` table and can be used for point-in-polygon lookup in future services.
- The legislative database readme is downloaded alongside other raw files to capture schema changes as they are published.
- Draft tables (`draft_*`) store the pre-validation data with the run date, while validated rows are promoted to the live tables.
- Validation issues are written to the `data_validation_issues` table for review.
- Session filtering keeps data within the configured lookback window (default: last three 2-year sessions).
