# TheLobby-App Requirements

## Project Overview
TheLobby-App is a full-stack application for tracking New Jersey legislative data. It consists of:
- **Frontend**: React Native/Expo mobile app with TypeScript
- **Backend**: Python pipeline for data synchronization
- **Admin Tools**: Node.js Supabase administration utilities

---

## Frontend Requirements (React Native/Expo)

### Core Runtime
- **Node.js**: 18.x or higher (recommended: 20.x LTS)
- **npm** or **yarn**: For package management

### Development Tools
- **Expo CLI**: Latest version (`npm install -g expo-cli`)
- **TypeScript**: ^5.x (via `@types/react`, `@types/react-native`)
- **ESLint**: ^9.25.0 (with Expo config)

### Key Dependencies
| Package | Version | Purpose |
|---------|---------|---------|
| `expo` | ~53.0.9 | App development framework |
| `react` | 19.0.0 | UI library |
| `react-native` | 0.79.2 | Native mobile framework |
| `expo-router` | ~5.0.6 | File-based routing |
| `@supabase/supabase-js` | ^2.49.4 | Backend database client |
| `@react-navigation/*` | Latest | Navigation stack |
| `@react-native-async-storage/async-storage` | 2.1.0 | Local data persistence |
| `expo-location` | ~18.1.1 | GPS/location services |
| `nativewind` | (implied) | Tailwind CSS for React Native |

### Platforms Supported
- iOS (via iOS Simulator or physical device)
- Android (via Android Emulator or physical device)
- Web (via browser)

---

## Backend Requirements (Python)

### Runtime
- **Python**: 3.9 or higher (recommended: 3.11+)
- **pip**: Package manager for Python

### Core Dependencies
| Package | Version | Purpose |
|---------|---------|---------|
| `requests` | >=2.28 | HTTP client for data downloads |
| `shapely` | >=2.0 | Geospatial geometries |
| `pyproj` | >=3.4 | Geographic projections |
| `geojson` | >=2.5 | GeoJSON data handling |
| `supabase` | >=1.0 | Supabase Python client |
| `python-dotenv` | >=1.0 | Environment variable management |
| `psycopg2-binary` | >=2.9 | PostgreSQL database adapter |
| `pytest` | >=7.0 | Testing framework |

### Data Processing Modules
- **Parsers**: Custom parsers for legislative data formats (CSV, TXT)
- **GIS**: ArcGIS client for legislative district data
- **Validators**: Data validation and schema enforcement

### Development & Testing
- `pytest` for unit and integration tests
- No linting requirement specified (recommend: `black`, `flake8`, `pylint`)

---

## Admin Tools (Node.js)

### Runtime
- **Node.js**: 18.x or higher

### Dependencies
| Package | Version | Purpose |
|---------|---------|---------|
| `@supabase/supabase-js` | ^2.45.4 | Supabase admin client |
| `dotenv` | ^16.4.5 | Environment configuration |

---

## System Requirements

### Local Development
| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **RAM** | 8 GB | 16 GB |
| **Disk Space** | 10 GB | 20 GB |
| **CPU Cores** | 4 | 8+ |

### Database
- **Supabase PostgreSQL**: Hosted on Supabase platform
- **Connection**: `postgresql://` with `psycopg2-binary`
- **Schema**: Managed via `schema.sql` in backend

### External APIs
- **NJ Legislative Downloads**: `https://www.njleg.state.nj.us/downloads`
- **Vote Data**: `https://pub.njleg.state.nj.us/votes`
- **GIS Service**: ArcGIS Feature Server (NJ Legislative Districts)

---

## Environment Configuration

### Backend Environment Variables
```bash
# NJ Legislature Data Sources
NJLEG_DOWNLOAD_BASE_URL=https://www.njleg.state.nj.us/downloads
NJLEG_DOWNLOAD_TYPE=Bill_Tracking
NJLEG_BILL_TRACKING_YEARS=2024
NJLEG_VOTES_BASE_URL=https://pub.njleg.state.nj.us/votes
NJLEG_VOTES_README_URL=https://pub.njleg.state.nj.us/votes/_Readme.txt
NJLEG_VOTES_COMM_README_URL=https://pub.njleg.state.nj.us/votes/_CommRdme.txt
NJLEG_GIS_SERVICE_URL=https://services2.arcgis.com/XVOqAjTOJ5P6ngMu/ArcGIS/rest/services/Legislative_Districts_of_NJ_Hosted_3424/FeatureServer/0
NJLEG_LEGDB_README_URL=https://pub.njleg.state.nj.us/leg-databases/2024data/Readme.txt
NJLEG_LEGDB_BASE_URL=https://pub.njleg.state.nj.us/leg-databases
NJLEG_LEGDB_YEARS=2024,2022,2020

# Supabase Configuration
SUPABASE_URL=<project-url>
SUPABASE_SERVICE_ROLE_KEY=<service-role-key>
SUPABASE_PUBLISHABLE_KEY=<publishable-key>

# Data Management
DATA_RETENTION_DAYS=3
BACKUP_RETENTION_COUNT=2
BACKUP_INTERVAL_DAYS=14
SESSION_LOOKBACK_COUNT=3
SESSION_LENGTH_YEARS=2
```

### Frontend Environment Variables
- **Supabase URL & Keys** (from backend)
- **Location services permissions** (iOS/Android)

### Admin Tools Environment Variables
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`

---

## Installation & Setup

### Frontend Setup
```bash
cd TheLobby-App
npm install
npm start
```

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Admin Tools Setup
```bash
cd supabase-admin
npm install
```

---

## Testing Requirements

### Backend Tests
- **Framework**: pytest >=7.0
- **Test Locations**: `backend/tests/` and `backend/gis/tests/`
- **Coverage**: Data validation, parsing, GIS operations

### Frontend Testing
- Manual testing on simulators/emulators
- Web testing via browser

---

## Deployment & CI/CD

### Recommended
- **Backend**: Deploy to cloud function (AWS Lambda, Google Cloud Functions, Azure Functions)
- **Frontend**: Build via Expo (`npx expo export --platform web`)
- **Admin Tools**: Deploy as serverless function or scheduled job

### Version Control
- Git repository management
- GitHub Actions (optional): For automated testing and deployments

---

## Additional Notes

- **Data Persistence**: Backend uses PostgreSQL via Supabase
- **Geospatial Needs**: Backend requires proj library for coordinate transformations
- **Development**: Mock/stub external APIs during local development
- **Performance**: Consider caching legislative data locally to reduce API calls
