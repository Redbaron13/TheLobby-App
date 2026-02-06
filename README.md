# Welcome to your Expo app 👋

This is an [Expo](https://expo.dev) project created with [`create-expo-app`](https://www.npmjs.com/package/create-expo-app).

## Get started

1. Install dependencies

   ```bash
   npm install
   ```

2. Start the app

   ```bash
   npx expo start
   ```

In the output, you'll find options to open the app in a

- [development build](https://docs.expo.dev/develop/development-builds/introduction/)
- [Android emulator](https://docs.expo.dev/workflow/android-studio-emulator/)
- [iOS simulator](https://docs.expo.dev/workflow/ios-simulator/)
- [Expo Go](https://expo.dev/go), a limited sandbox for trying out app development with Expo

You can start developing by editing the files inside the **app** directory. This project uses [file-based routing](https://docs.expo.dev/router/introduction).

## Get a fresh project

When you're ready, run:

```bash
npm run reset-project
```

This command will move the starter code to the **app-example** directory and create a blank **app** directory where you can start developing.

## Learn more

To learn more about developing your project with Expo, look at the following resources:

- [Expo documentation](https://docs.expo.dev/): Learn fundamentals, or go into advanced topics with our [guides](https://docs.expo.dev/guides).
- [Learn Expo tutorial](https://docs.expo.dev/tutorial/introduction/): Follow a step-by-step tutorial where you'll create a project that runs on Android, iOS, and the web.

## Join the community

Join our community of developers creating universal apps.

- [Expo on GitHub](https://github.com/expo/expo): View our open source platform and contribute.
- [Discord community](https://chat.expo.dev): Chat with Expo users and ask questions.

---

## 🚀 Quick Start (One-Step Setup)

The easiest way to get started is to use the provided setup script:

```bash
./setup.sh
```

This script will:
1. Check for required dependencies (Node, Python, Docker).
2. Install frontend and backend dependencies.
3. Create environment variable files from templates.
4. Optionally initialize your Supabase database schema.
5. Verify your setup with a validation script.

---

## 🐳 Running with Docker

You can run the entire application stack using Docker Compose. This is the recommended way for production or consistent testing environments.

1. Ensure your environment variables are set in `.env.local` and `backend/.env`.
2. Run the following command:

```bash
docker-compose up --build
```

- **Frontend:** Accessible at [http://localhost:8081](http://localhost:8081)
- **Backend API:** Accessible at [http://localhost:8000](http://localhost:8000)

---

## 💻 Local Development

### Backend (Python API & Data Pipeline)

The backend provides a FastAPI server that handles data synchronization and database management.

1. **Install Dependencies:**
   ```bash
   pip install -r backend/requirements.txt
   ```
2. **Run the API:**
   ```bash
   PYTHONPATH=. uvicorn backend.api:app --reload
   ```

### Frontend (Expo App)

1. **Install Dependencies:**
   ```bash
   npm install
   ```
2. **Start Expo:**
   ```bash
   npx expo start --web
   ```

---

## 🛠️ Admin Dashboard

The application includes an Admin Dashboard for managing the backend and monitoring data quality.

- **Access:** Navigate to `/admin` in the Expo app.
- **Features:**
  - **Run Data Sync:** Manually trigger the NJ Legislature data pipeline.
  - **Init Database:** Initialize the Supabase schema (use with caution).
  - **Monitor Issues:** View and filter data validation issues identified during the sync process.

---

## 📖 Maintenance & Understanding

### Backend Data Sync
The backend pipeline downloads NJ Legislature data daily, cleans it, and pushes changes into Supabase. See `backend/README.md` for detailed architecture and scheduling instructions.

### Feature Flags
You can enable/disable features via environment variables:
- `EXPO_PUBLIC_ENABLE_LOCATION`: Enable/disable the "Find Your Legislator" GPS feature.

### Troubleshooting
- **Module Resolution Error:** If you see "Unable to resolve module ../utils/supabase", ensure you are using the correct imports from `@/app/lib/supabase`.
- **Database Connection:** Verify `SUPABASE_DB_URL` is correctly set in `backend/.env` for initialization tasks.

---

## 🧪 Testing

### Run Backend Tests
```bash
PYTHONPATH=. python3 -m pytest backend/tests/
```

### Run Setup Validation
```bash
bash scripts/validate-env.sh
```
