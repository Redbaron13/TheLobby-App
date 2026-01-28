################################################################################
# ENVIRONMENT VARIABLE CONSISTENCY GUIDE
################################################################################

This document explains all environment variables used in TheLobby-App and how 
to keep them consistent across the codebase.

## File Structure & Locations

```
TheLobby-App/
├── .env.example                    # Frontend env template (Expo)
├── supabase-admin/
│   ├── .env                        # Admin tool secrets (PRIVATE)
│   └── example-env.md              # Admin template
├── backend/
│   └── .env.example                # Backend env template
└── app/lib/supabase.ts             # Frontend config loader
```

## Environment Variable Categories

### 1. SUPABASE CONFIGURATION
All three components (frontend, backend, admin) need Supabase credentials.

**Frontend (Expo)** - Client-side keys only:
```bash
EXPO_PUBLIC_SUPABASE_URL=https://zgtevahaudnjpocptzgj.supabase.co
EXPO_PUBLIC_SUPABASE_ANON_KEY=<anon-key>
```

**Backend (Python)** - Server-side keys:
```bash
SUPABASE_URL=https://zgtevahaudnjpocptzgj.supabase.co
SUPABASE_SERVICE_ROLE_KEY=<service-role-key>
```

**Admin Tools (Node.js)** - Server-side keys:
```bash
SUPABASE_URL=https://zgtevahaudnjpocptzgj.supabase.co
SUPABASE_SERVICE_ROLE_KEY=<service-role-key>
```

### 2. NJ LEGISLATURE DATA PIPELINE (Backend only)

```bash
# Data sources
NJLEG_DOWNLOAD_BASE_URL=https://www.njleg.state.nj.us/downloads
NJLEG_DOWNLOAD_TYPE=Bill_Tracking
NJLEG_BILL_TRACKING_YEARS=2024
NJLEG_VOTES_BASE_URL=https://pub.njleg.state.nj.us/votes
NJLEG_VOTES_README_URL=https://pub.njleg.state.nj.us/votes/_Readme.txt
NJLEG_VOTES_COMM_README_URL=https://pub.njleg.state.nj.us/votes/_CommRdme.txt

# GIS/Districts
NJLEG_GIS_SERVICE_URL=https://services2.arcgis.com/XVOqAjTOJ5P6ngMu/ArcGIS/rest/services/Legislative_Districts_of_NJ_Hosted_3424/FeatureServer/0

# Legislative database
NJLEG_LEGDB_BASE_URL=https://pub.njleg.state.nj.us/leg-databases
NJLEG_LEGDB_README_URL=https://pub.njleg.state.nj.us/leg-databases/2024data/Readme.txt
NJLEG_LEGDB_YEARS=2024,2022,2020
```

### 3. DATA RETENTION POLICIES (Backend only)

```bash
DATA_RETENTION_DAYS=3                 # Keep 3 days of history
BACKUP_RETENTION_COUNT=2              # Keep 2 backups
BACKUP_INTERVAL_DAYS=14               # Backup every 14 days
SESSION_LOOKBACK_COUNT=3              # Look back 3 sessions
SESSION_LENGTH_YEARS=2                # Each session is 2 years
```

### 4. FILE STORAGE (Backend only)

```bash
NJLEG_DATA_DIR=backend/data           # Downloaded data storage
DATABASE_URL=postgresql://...         # Optional direct DB connection
```

## Security Best Practices

### DO's ✅
- Store actual API keys in environment variables or secret management tools
- Commit `.env.example` and `.env` template files to git
- Use `EXPO_PUBLIC_` prefix for frontend environment variables (these are public)
- Use `SUPABASE_SERVICE_ROLE_KEY` only on the backend

### DON'Ts ❌
- Never commit actual `.env` files with real secrets
- Never share `SUPABASE_SERVICE_ROLE_KEY` or expose it client-side
- Never hardcode secrets in source code
- Don't put service keys in frontend code

## How Each Component Reads Configuration

### Frontend (React Native/Expo)
**File:** `app/lib/supabase.ts`

```typescript
const supabaseUrl = process.env.EXPO_PUBLIC_SUPABASE_URL ?? '';
const supabaseKey = process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY ?? '';
```

Requires environment variables to start with `EXPO_PUBLIC_` prefix.

### Backend (Python)
**File:** `backend/config.py`

```python
supabase_url = os.getenv("SUPABASE_URL", "https://zgtevahaudnjpocptzgj.supabase.co")
supabase_service_key = _resolve_supabase_key()  # Checks multiple key names
```

Falls back to hardcoded URL but requires actual key from environment.

Key resolution order: `SUPABASE_SERVICE_ROLE_KEY` → `SUPABASE_PUBLISHABLE_KEY` → `SUPABASE_ANON_KEY`

### Admin Tools (Node.js)
**File:** `supabase-admin/index.js`

```javascript
require('dotenv').config();
// Uses process.env.SUPABASE_URL and process.env.SUPABASE_SERVICE_ROLE_KEY
```

## Setup Instructions

### 1. Development Setup

```bash
# Frontend
cp .env.example .env.local
# Edit .env.local with your Supabase anon key

# Backend
cd backend
cp .env.example .env
# Edit .env with your Supabase service role key and data settings

# Admin tools
cd supabase-admin
# .env is already configured with secrets
```

### 2. CI/CD Setup

Use GitHub Actions secrets or your CI platform's secret management:

```yaml
# GitHub Actions example
env:
  SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
  SUPABASE_SERVICE_ROLE_KEY: ${{ secrets.SUPABASE_SERVICE_ROLE_KEY }}
  NJLEG_BILL_TRACKING_YEARS: "2024"
  # ... other variables
```

### 3. Production Deployment

```bash
# Set as environment variables on your deployment platform
# Examples:
# - AWS Lambda: Set in Lambda environment variables
# - Heroku: Use heroku config:set
# - Docker: Pass via -e flag or docker-compose.yml
# - Vercel/Netlify: Use dashboard settings
```

## Verification Checklist

Before deploying or committing, verify:

- [ ] `.env` file is in `.gitignore` (don't commit secrets)
- [ ] `.env.example` has template values (safe to commit)
- [ ] Frontend uses `EXPO_PUBLIC_` prefix for public keys
- [ ] Backend has `SUPABASE_SERVICE_ROLE_KEY` set
- [ ] All NJLEG URLs are correct for current session
- [ ] Data retention settings match your requirements
- [ ] No hardcoded secrets in source files

## Troubleshooting

### Frontend can't connect to Supabase
- Check `EXPO_PUBLIC_SUPABASE_URL` and `EXPO_PUBLIC_SUPABASE_ANON_KEY` are set
- Ensure variables start with `EXPO_PUBLIC_`
- Rebuild the app after changing env vars

### Backend can't authenticate
- Verify `SUPABASE_URL` is correct
- Ensure `SUPABASE_SERVICE_ROLE_KEY` is set and valid
- Check key hasn't expired in Supabase dashboard

### Admin tools can't run
- Confirm `supabase-admin/.env` exists with real credentials
- Verify node_modules are installed: `npm install`
- Check permissions on .env file

## References

- [Expo Environment Variables](https://docs.expo.dev/build-reference/variables/)
- [Supabase Authentication](https://supabase.com/docs/guides/auth)
- [Backend Config Module](backend/config.py)
- [Frontend Supabase Client](app/lib/supabase.ts)
