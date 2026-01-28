# Environment Configuration Update Summary

## Overview
All environment variables across the TheLobby-App codebase have been standardized and made consistent with the `REQUIREMENTS.md` file. This ensures that frontend, backend, and admin tools can work together seamlessly.

## Files Created/Updated

### 📄 Main Configuration Files

1. **`.env.example`** (NEW)
   - Frontend/Expo environment template
   - Contains client-side Supabase variables with `EXPO_PUBLIC_` prefix
   - Safe to commit to git

2. **`backend/.env.example`** (NEW)
   - Backend Python environment template
   - Contains all NJ Legislature data pipeline configuration
   - Includes Supabase service role key template
   - Safe to commit to git

3. **`supabase-admin/.env`** (UPDATED)
   - Reorganized with clear sections
   - Added comprehensive comments explaining each variable
   - Added legacy key support for backward compatibility
   - Includes actual service credentials

4. **`supabase-admin/example-env.md`** (UPDATED)
   - Simplified template structure
   - Added security warnings and best practices
   - Clear instructions for setup

### 📚 Documentation Files

5. **`ENV_VARIABLES.md`** (NEW)
   - Comprehensive environment variable guide
   - Explains how each component reads configuration
   - Security best practices
   - Troubleshooting section
   - Verification checklist
   - References to source code

6. **`.gitignore.template`** (NEW)
   - Recommended `.gitignore` entries
   - Covers environment files, build artifacts, Python/Node caches
   - Backend data directories
   - IDE and OS files

7. **`scripts/validate-env.sh`** (NEW)
   - Bash script to validate environment setup
   - Checks all required variables
   - Verifies consistency between components
   - Provides setup instructions

## Key Changes

### Naming Consistency
- **Frontend:** Uses `EXPO_PUBLIC_` prefix (Expo requirement)
  - `EXPO_PUBLIC_SUPABASE_URL`
  - `EXPO_PUBLIC_SUPABASE_ANON_KEY`

- **Backend:** Uses standard variable names
  - `SUPABASE_URL`
  - `SUPABASE_SERVICE_ROLE_KEY` (primary)
  - Falls back to `SUPABASE_PUBLISHABLE_KEY` and `SUPABASE_ANON_KEY`

- **Admin Tools:** Uses consistent naming with backend
  - `SUPABASE_URL`
  - `SUPABASE_SERVICE_ROLE_KEY`

### Security Improvements
- Clear distinction between client-side (public) and server-side (secret) keys
- Comments warn against exposing service role keys
- Template files use placeholder values (`your-*`) instead of real keys
- Organized sections for easy identification of sensitive variables

### Backend Configuration Standardization
All variables from `backend/config.py` are now documented:

```bash
# Data Sources
NJLEG_DOWNLOAD_BASE_URL
NJLEG_DOWNLOAD_TYPE
NJLEG_BILL_TRACKING_YEARS
NJLEG_VOTES_BASE_URL
NJLEG_VOTES_README_URL
NJLEG_VOTES_COMM_README_URL
NJLEG_GIS_SERVICE_URL
NJLEG_LEGDB_BASE_URL
NJLEG_LEGDB_README_URL
NJLEG_LEGDB_YEARS

# Data Management
DATA_RETENTION_DAYS
BACKUP_RETENTION_COUNT
BACKUP_INTERVAL_DAYS
SESSION_LOOKBACK_COUNT
SESSION_LENGTH_YEARS
```

## Component Configuration Sources

### Frontend (React Native/Expo)
- **File:** `app/lib/supabase.ts`
- **Env Source:** `.env.local` or `.env.example`
- **Key Variables:** `EXPO_PUBLIC_SUPABASE_*`

### Backend (Python)
- **File:** `backend/config.py`
- **Env Source:** `backend/.env` or `backend/.env.example`
- **Key Variables:** `SUPABASE_*`, `NJLEG_*`, `DATA_*`

### Admin Tools (Node.js)
- **File:** `supabase-admin/index.js`
- **Env Source:** `supabase-admin/.env`
- **Key Variables:** `SUPABASE_*`

## Setup Instructions for Developers

### 1. Clone Repository
```bash
git clone https://github.com/Redbaron13/TheLobby-App.git
cd TheLobby-App
```

### 2. Frontend Setup
```bash
# Copy environment template
cp .env.example .env.local

# Edit with your Supabase credentials
# (anon key only - safe for client)
```

### 3. Backend Setup
```bash
cd backend
cp .env.example .env

# Edit with:
# - SUPABASE_SERVICE_ROLE_KEY (secret!)
# - NJLEG_BILL_TRACKING_YEARS and other data settings
```

### 4. Admin Tools Setup
```bash
cd supabase-admin
# .env file already exists with credentials
# (Verify credentials match other components)
```

### 5. Validate Setup
```bash
# From project root
bash scripts/validate-env.sh
```

## CI/CD Integration

For automated deployments, configure these secrets in your CI platform:

**GitHub Actions Example:**
```yaml
- name: Build Backend
  env:
    SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
    SUPABASE_SERVICE_ROLE_KEY: ${{ secrets.SUPABASE_SERVICE_ROLE_KEY }}
    NJLEG_BILL_TRACKING_YEARS: "2024"
```

## Security Checklist

Before deploying:
- [ ] `.env` files are in `.gitignore`
- [ ] `.env.example` files contain only template values
- [ ] No real secrets in source code
- [ ] Service role keys are only used on backend
- [ ] Frontend only has anonymous/publishable keys
- [ ] All environment variables validated with `validate-env.sh`

## Verification

All variables are consistent with:
- ✅ `REQUIREMENTS.md` - Documentation matches
- ✅ `backend/config.py` - Backend reads all variables
- ✅ `app/lib/supabase.ts` - Frontend reads Supabase config
- ✅ Supabase project dashboard - Credentials are valid

## Next Steps

1. **For Local Development:**
   - Copy `.env.example` to `.env.local`
   - Copy `backend/.env.example` to `backend/.env`
   - Fill in with your actual credentials
   - Run validation script

2. **For Team:**
   - Share `.env.example` files with team (no secrets)
   - Each developer creates their own `.env*` files locally
   - Never commit `.env` files

3. **For Production:**
   - Use secret management (GitHub Secrets, HashiCorp Vault, etc.)
   - Configure environment variables on deployment platform
   - Rotate keys regularly

## References

- [REQUIREMENTS.md](REQUIREMENTS.md) - Full project requirements
- [ENV_VARIABLES.md](ENV_VARIABLES.md) - Detailed environment guide
- [backend/config.py](backend/config.py) - Backend configuration loading
- [app/lib/supabase.ts](app/lib/supabase.ts) - Frontend Supabase client
- [Expo Environment Variables](https://docs.expo.dev/build-reference/variables/)
- [Supabase Authentication](https://supabase.com/docs/guides/auth)
