
# Autonomous Agents & Services Guide

This document describes all autonomous agents, workers, and services in TheLobby-App. These are the background systems that process data, sync with external services, and maintain the application state.

---

## Table of Contents

1. [Data Pipeline Agents (Backend)](#data-pipeline-agents-backend)
2. [Frontend Services](#frontend-services)
3. [Admin Services](#admin-services)
4. [Agent Orchestration](#agent-orchestration)
5. [Scheduled Execution](#scheduled-execution)
6. [Error Handling & Retry Logic](#error-handling--retry-logic)
7. [Monitoring & Logging](#monitoring--logging)

---

## Data Pipeline Agents (Backend)

The backend contains a series of coordinated agents that collectively sync New Jersey legislative data from various sources to Supabase.

### 1. **Legislative Downloader Agent**
**File:** `backend/legislative_downloads.py` & `backend/legdb_downloader.py`

**Responsibility:** Download legislative data files from external sources

**Process:**
```
NJ Legislature Website → HTML parsing → Find data files → Download to disk
```

**Key Functions:**
- `download_bill_tracking_session()` - Downloads MAINBILL.TXT, ROSTER.TXT, etc.
- `download_legdb_session()` - Downloads legislative database records for historical sessions
- `fetch_index_html()` - Parses HTML to locate downloadable files

**Configuration:** 
- Sources: `NJLEG_DOWNLOAD_BASE_URL`, `NJLEG_LEGDB_BASE_URL`
- Years: `NJLEG_BILL_TRACKING_YEARS`, `NJLEG_LEGDB_YEARS`
- Output: `backend/data/` directory

**Dependencies:** `urllib`, `requests`

**Error Scenarios:**
- File not found on server
- Network timeout
- Invalid HTML structure

---

### 2. **Votes Downloader Agent**
**File:** `backend/votes_downloader.py`

**Responsibility:** Discover and download legislative vote records

**Process:**
```
Vote Index Files → Parse README files → Identify vote CSV files → Download all
```

**Key Functions:**
- `download_votes()` - Main orchestration function
- Discovers voting records from readme files at:
  - `https://pub.njleg.state.nj.us/votes/_Readme.txt`
  - `https://pub.njleg.state.nj.us/votes/_CommRdme.txt`

**Configuration:**
- `NJLEG_VOTES_BASE_URL`
- `NJLEG_VOTES_README_URL`
- `NJLEG_VOTES_COMM_README_URL`

**Output:** Vote record files in `backend/data/`

---

### 3. **GIS/Spatial Data Agent**
**File:** `backend/gis/arcgis_client.py`, `backend/gis/repository.py`

**Responsibility:** Fetch and validate legislative district boundary data

**Process:**
```
ArcGIS Feature Server → Query geographic data → Validate geometries → Transform coordinates
```

**Key Functions:**
- `fetch_all_features()` - Paginates through ArcGIS feature server
- `fetch_layer_metadata()` - Retrieves layer information and validates schema
- `_query_params()` - Builds ArcGIS query parameters

**Configuration:**
- `NJLEG_GIS_SERVICE_URL` - ArcGIS Feature Server endpoint
- Geometry validation ensures polygon/multipolygon types
- Spatial reference validation (WKID checking)

**Dependencies:** `requests`, `geojson`, `shapely`, `pyproj`

**Output:** Validated GIS features in GeoJSON format

**Validation Checks:**
- Geometry type validation (must be polygon/multipolygon)
- Spatial reference WKID existence
- Coordinate system transformations

---

### 4. **Data Parser Agents**
**Directory:** `backend/parsers/`

**Responsibility:** Transform raw text files into structured data

**Parser Types:**

#### 4a. **MAINBILL Parser**
**File:** `backend/parsers/mainbill.py`
- Parses bill tracking data
- Outputs: bill records with status, sponsors, history
- Handles special characters and encoding issues

#### 4b. **ROSTER Parser**
**File:** `backend/parsers/roster.py`
- Parses legislator records
- Outputs: legislator details (name, chamber, district, contact)
- Handles data normalization and cleanup

#### 4c. **BILLSPON Parser**
**File:** `backend/parsers/billspon.py`
- Parses bill sponsorship relationships
- Outputs: bill sponsor records linking bills to legislators

#### 4d. **COMEMBER Parser**
**File:** `backend/parsers/commember.py`
- Parses committee membership records
- Outputs: committee member records

#### 4e. **Vote Parser**
**File:** `backend/parsers/votes.py`
- Parses vote record CSV files
- Outputs: structured voting records per legislator per bill

#### 4f. **District Parser**
**File:** `backend/parsers/districts.py`
- Parses GIS geographic data
- Converts GeoJSON to database records
- Extracts district metadata

**Common Features:**
- UTF-8 encoding handling
- Row validation
- Key normalization (e.g., `normalize_string()`)
- Null/empty field handling

---

### 5. **Data Validation Agent**
**File:** `backend/validation.py`

**Responsibility:** Validate data quality before persisting to database

**Validation Functions:**

```python
validate_bills()              # Check bill records integrity
validate_legislators()        # Validate legislator data
validate_bill_sponsors()      # Verify sponsor relationships
validate_committee_members()  # Check committee data
validate_vote_records()       # Validate vote records
validate_districts()          # Validate geographic data
filter_to_recent_sessions()   # Filter by date window
```

**Process:**
```
Parsed data → Validation rules → Issues collection → Valid rows + Issues list
```

**Validation Checks:**
- Date range validation (remove old sessions)
- Key field presence
- Relationship integrity (sponsors exist, bills exist)
- Data type validation
- Geographic bounds checking

**Output:** 
- `valid_rows`: Data that passed validation
- `issues`: `ValidationIssue` records for audit trail

---

### 6. **Data Merge & Deduplication Agent**
**File:** `backend/data_merge.py`

**Responsibility:** Combine data from multiple sources and handle updates

**Process:**
```
New data + Existing snapshots → Merge by key → Deduplicate → Resolve conflicts
```

**Key Functions:**
- `merge_rows_by_key()` - Combines rows using primary keys
- Handles NEW, UPDATED, and DELETED records
- Maintains historical snapshots

**Merge Strategy:**
- Uses PRIMARY_KEYS mapping (bills→bill_key, legislators→roster_key, etc.)
- Newer data overwrites older
- Tracks change history for audit

---

### 7. **Session Filtering Agent**
**File:** `backend/session_filter.py`

**Responsibility:** Filter data to relevant legislative sessions

**Configuration:**
- `SESSION_LOOKBACK_COUNT` - Number of sessions to include (default: 3)
- `SESSION_LENGTH_YEARS` - Years per session (default: 2)

**Process:**
```
Current date → Calculate session window → Filter records by session dates
```

**Output:** Records filtered to relevant sessions only

---

### 8. **Snapshot Management Agent**
**File:** `backend/snapshot.py`

**Responsibility:** Create and manage versioned backups of data

**Key Functions:**
- `create_backup()` - Creates timestamped backup
- `load_latest_snapshot()` - Retrieves previous version
- `enforce_retention()` - Deletes old backups
- `should_create_backup()` - Determines backup necessity

**Backup Policy:**
- Location: `backend/backups/` directory
- `BACKUP_RETENTION_COUNT` - Keep N backups (default: 2)
- `BACKUP_INTERVAL_DAYS` - Create backup every N days (default: 14)
- Format: Timestamped JSON snapshots

**Purpose:**
- Recovery from data corruption
- Audit trail
- Rollback capability

---

### 9. **Supabase Persistence Agent**
**File:** `backend/supabase_loader.py`

**Responsibility:** Persist validated data to database

**Key Functions:**
```python
SupabaseClient.upsert(table, rows, batch_size=500)
```

**Process:**
```
Valid data → Batch into 500-row chunks → HTTP POST to Supabase REST API
```

**Database Operations:**
- Upsert (insert or update on conflict)
- Batch processing for efficiency
- Retry logic for failed batches

**Configuration:**
- `SUPABASE_URL` - Database URL
- `SUPABASE_SERVICE_ROLE_KEY` - Authentication key

**API Headers:**
```
Authorization: Bearer {service_key}
Prefer: resolution=merge-duplicates,return=representation
```

---

### 10. **Master Pipeline Orchestrator Agent**
**File:** `backend/pipeline.py`

**Responsibility:** Coordinate all agents in correct sequence

**Execution Flow:**

```
┌─────────────────────────────────────┐
│ run_pipeline(config, date)          │
├─────────────────────────────────────┤
│ 1. Load config & initialize         │
│ 2. Download legislation files       │
│ 3. Download votes files             │
│ 4. Fetch GIS data                   │
│ 5. Parse all data                   │
│ 6. Validate records                 │
│ 7. Split legislators (active/former)│
│ 8. Merge with existing data         │
│ 9. Check backup threshold           │
│ 10. Persist to Supabase             │
│ 11. Create backup if needed         │
│ 12. Enforce retention policy        │
│ 13. Return results summary          │
└─────────────────────────────────────┘
```

**Key Function:**
```python
def run_pipeline(config: PipelineConfig, run_date: str | None = None) -> PipelineResult:
    # Returns counts for all tables processed
```

**Output:**
```python
@dataclass
class PipelineResult:
    bills: int                  # Bills processed
    legislators: int            # Active legislators
    former_legislators: int     # Former legislators
    bill_sponsors: int          # Sponsor relationships
    committee_members: int      # Committee memberships
    vote_records: int           # Vote records
    districts: int              # Geographic districts
    validation_issues: int      # Data quality issues
```

---

## Frontend Services

### 1. **Supabase Client Service**
**File:** `app/lib/supabase.ts`

**Responsibility:** Manage connection to Supabase database

**Features:**
- Real-time subscription capability
- Authentication state management
- Query optimization for mobile network

**Configuration:**
```typescript
const supabaseUrl = process.env.EXPO_PUBLIC_SUPABASE_URL
const supabaseKey = process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY
```

**Exported:**
```typescript
export const supabase: SupabaseClient | null
export const isSupabaseConfigured: boolean
```

---

### 2. **Location Service Agent** (Passive)
**File:** `app/find-legislator.tsx`

**Responsibility:** Get user location for legislator lookup

**Capabilities:**
- GPS coordinate retrieval
- District lookup by location
- Legislator matching by district

**Permissions Required:**
- `expo-location` - Location access
- iOS/Android location permission dialogs

---

### 3. **Data Display Services**
**Components:** Various screens in `app/` and `components/`

**Services:**
- Bill list display & filtering
- Legislator profile view
- Committee structure visualization
- Vote record display
- Chamber-based views (Assembly, Senate)

---

## Admin Services

### 1. **Supabase Admin Client**
**File:** `supabase-admin/index.js`

**Responsibility:** Provide server-side administration capabilities

**Capabilities:**
- User management
- Database schema administration
- Policy management
- Custom function execution
- Data export/import

**Configuration:**
- Requires `SUPABASE_SERVICE_ROLE_KEY` (full admin access)
- `SUPABASE_URL` endpoint

---

## Agent Orchestration

### Entry Points

1. **Manual Sync**
```bash
python -m backend.run_sync [--date YYYY-MM-DD]
```
- Runs full pipeline once
- Optional date override for testing

2. **Scheduled Execution** (Recommended)
```bash
# GitHub Actions, cron, Lambda, etc.
# Runs daily or on schedule
```

3. **Schema Initialization**
```bash
python -m backend.init_supabase
```
- Creates database schema on first setup
- Idempotent (safe to run multiple times)

---

## Scheduled Execution

Recommended setup for production:

### GitHub Actions (Recommended)
```yaml
name: Sync Legislature Data
on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM UTC

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r backend/requirements.txt
      - name: Run sync
        env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_SERVICE_ROLE_KEY: ${{ secrets.SUPABASE_SERVICE_ROLE_KEY }}
          # ... other env vars
        run: python -m backend.run_sync
```

### Alternative Platforms
- **AWS Lambda:** CloudWatch Events trigger
- **Google Cloud Functions:** Cloud Scheduler trigger
- **Azure Functions:** Timer trigger
- **Heroku:** Scheduler add-on
- **VPS/Server:** Cron job

---

## Error Handling & Retry Logic

### Downloader Agent
- Network timeouts trigger retry (default: 3 attempts)
- File not found error is fatal

### Parser Agents
- Skip malformed rows, log issues
- Continue processing remaining rows
- Report summary in validation issues

### Validation Agent
- Issues don't stop pipeline
- All validation issues persisted to audit table
- Logging allows debugging

### Supabase Persistence
- Batch failures retry individually
- Timeout handling (30s per batch)
- Connection pooling

### Pipeline Orchestrator
- Full pipeline rollback on critical failure
- Failed rows logged for manual review
- Backup only created if all steps succeed

---

## Monitoring & Logging

### Logging Strategy

**Pipeline Results Summary:**
```
Sync complete.
Bills: 2,456
Legislators: 150
Former legislators: 85
Bill sponsors: 8,923
Committee members: 1,234
Vote records: 45,678
Districts: 40
Validation issues: 12
```

### Audit Trail

All validation issues persisted to database:
```python
@dataclass
class ValidationIssue:
    table: str              # bills, legislators, etc.
    record_key: str | None  # Primary key of problem record
    issue: str              # Issue type
    details: str | None     # Additional context
    run_date: str | None    # When detected
```

### Monitoring Recommendations

1. **Success Rate Tracking**
   - Track validation_issues count
   - Alert if > threshold

2. **Data Volume Validation**
   - Bills count should stay relatively stable
   - Alert if dramatic changes

3. **Backup Health**
   - Verify backups created on schedule
   - Check backup retention working

4. **Runtime Monitoring**
   - Pipeline should complete in < 5 minutes
   - Alert on timeout

---

## Configuration Matrix

| Agent | Config Vars | Timeout | Retry |
|-------|------------|---------|-------|
| Legislative Downloader | NJLEG_* | 30s | 3x |
| Votes Downloader | NJLEG_VOTES_* | 30s | 3x |
| GIS Agent | NJLEG_GIS_* | 30s | 1x |
| Parser Agents | N/A | N/A | N/A |
| Validation Agent | SESSION_* | N/A | N/A |
| Snapshot Agent | BACKUP_* | N/A | N/A |
| Supabase Agent | SUPABASE_* | 30s | Per batch |

---

## Data Flow Diagram

```
External Sources:
┌─ NJ Legislature Website (MAINBILL, ROSTER, etc.)
├─ Vote Records Server
└─ ArcGIS Feature Server

     ↓

Backend Agents:
┌─────────────────────────────────┐
│ Downloader Agents               │
│ (fetch raw files/data)          │
└──────────┬──────────────────────┘
           ↓
┌─────────────────────────────────┐
│ Parser Agents                   │
│ (transform to structured data)  │
└──────────┬──────────────────────┘
           ↓
┌─────────────────────────────────┐
│ Validation Agent                │
│ (check data quality)            │
└──────────┬──────────────────────┘
           ↓
┌─────────────────────────────────┐
│ Merge Agent                     │
│ (combine with existing data)    │
└──────────┬──────────────────────┘
           ↓
┌─────────────────────────────────┐
│ Snapshot Agent                  │
│ (backup if needed)              │
└──────────┬──────────────────────┘
           ↓
┌─────────────────────────────────┐
│ Supabase Persistence            │
│ (upsert to database)            │
└─────────────────────────────────┘
           ↓
        Supabase PostgreSQL Database
           ↓
      ↙─────────────────╲
     ↙                   ╲
Frontend App          Admin Tools
(React Native)        (Node.js)
```

---

## API Contracts

### Downloader → Parser
```python
Input: file_path: Path
Output: list[dict]  # Parsed records
```

### Parser → Validation
```python
Input: list[dict]   # Parsed records
Output: ValidationResult
  - valid_rows: list[dict]
  - issues: list[ValidationIssue]
```

### Validation → Merge
```python
Input: valid_rows, existing_snapshot
Output: merged_rows with change markers (NEW, UPDATED, DELETED)
```

### Merge → Supabase
```python
Input: merged_rows
Output: None (side effect: database upsert)
```

---

## Testing Agents

### Unit Tests
```bash
pytest backend/tests/
```

Tests include:
- Parser validation
- Data type checking
- Encoding handling
- Session filtering logic

### Integration Tests
```bash
pytest backend/tests/test_gis_validation.py
```

Tests include:
- GIS validation with real/mock data
- Projection transformations
- Full pipeline simulation

### Manual Testing
```bash
# Test with specific date (doesn't sync live data)
python -m backend.run_sync --date 2024-01-15

# Test with mocked services
export NJLEG_DOWNLOAD_BASE_URL=file:///test/data/
python -m backend.run_sync
```

---

## Future Agent Opportunities

1. **Change Detection Agent**
   - Monitor for specific legislator changes
   - Push notifications to interested users

2. **Historical Analysis Agent**
   - Track voting patterns over time
   - Identify legislators' position changes

3. **Bill Tracking Agent**
   - Watch specific bills through legislature
   - Alert on status changes

4. **Recommendation Agent**
   - Suggest similar bills to users
   - Recommend legislators by district

---

## References

- [Backend Config](backend/config.py) - Configuration loading
- [Pipeline Orchestration](backend/pipeline.py) - Main pipeline
- [Validation Logic](backend/validation.py) - Validation rules
- [Frontend Supabase](app/lib/supabase.ts) - Frontend service
- [ENV_VARIABLES.md](ENV_VARIABLES.md) - Configuration guide
