# NJ Legislature Data Pipeline

This backend module downloads NJ Legislature data files, cleans them, and upserts changes into Supabase. It is designed to run daily (via cron, GitHub Actions, or a server job) and only pushes changed rows while keeping a small rolling history and periodic backups.

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
export NJLEG_VOTES_BASE_URL="https://pub.njleg.state.nj.us/votes"
export NJLEG_VOTES_README_URL="https://pub.njleg.state.nj.us/votes/_Readme.txt"
export NJLEG_VOTES_COMM_README_URL="https://pub.njleg.state.nj.us/votes/_CommRdme.txt"
export NJLEG_GIS_SERVICE_URL="https://services2.arcgis.com/XVOqAjTOJ5P6ngMu/ArcGIS/rest/services/Legislative_Districts_of_NJ_Hosted_3424/FeatureServer/0"
export NJLEG_LEGDB_README_URL="https://pub.njleg.state.nj.us/leg-databases/2024data/Readme.txt"
export SUPABASE_URL="https://<project>.supabase.co"
export SUPABASE_SERVICE_ROLE_KEY="<service-role-key>"
export DATA_RETENTION_DAYS=3
export BACKUP_RETENTION_COUNT=2
export BACKUP_INTERVAL_DAYS=14
```

## Run a Manual Sync

```bash
python backend/run_sync.py
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

## Supabase Tables

Use `backend/schema.sql` to create the tables and indexes in Supabase before running the sync.

## Notes
- The pipeline stores raw downloads in `backend/data/raw/<YYYY-MM-DD>/` and processed snapshots in `backend/data/processed/<YYYY-MM-DD>/`.
- Only changed rows are upserted to Supabase by comparing row hashes against the previous snapshot.
- Backups capture full datasets on a schedule and are retained separately to guard against data corruption.
- Vote files are stored in `backend/data/raw/<YYYY-MM-DD>/votes/` and parsed into a `vote_records` table with raw payloads for forward-compatible schema updates.
- GIS district polygons are stored as GeoJSON in the `districts` table and can be used for point-in-polygon lookup in future services.
- The legislative database readme is downloaded alongside other raw files to capture schema changes as they are published.
