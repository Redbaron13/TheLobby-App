
# Local Development Setup Guide

This guide explains how to set up the project locally using Docker Compose, including a local Postgres database, PostgREST for data access, and Nginx as a reverse proxy.

## Prerequisites
- Docker and Docker Compose installed on your machine.

## Architecture
- **Frontend**: Expo web app (React Native).
- **Backend**: Python FastAPI app for data pipeline and custom endpoints.
- **Database**: Postgres 15 (mimicking Supabase DB).
- **PostgREST**: Provides RESTful API over Postgres (compatible with Supabase client).
- **Nginx**: Reverse proxy routing requests to Backend (`/api/`) and PostgREST (`/rest/v1/`).

## Steps

1.  **Start the Local Stack**:
    Run the following command to spin up all services:
    ```bash
    docker-compose -f docker-compose.local.yml up --build
    ```

2.  **Initialize the Database**:
    Once the containers are running, you need to initialize the database schema and roles (for PostgREST).

    Open a new terminal and run:
    ```bash
    docker-compose -f docker-compose.local.yml exec backend python -m backend.init_supabase
    ```
    This script will:
    - Create the necessary tables.
    - Create `anon` and `authenticated` roles for PostgREST security.

3.  **Access the Application**:
    -   **Frontend**: http://localhost
    -   **Backend API Docs**: http://localhost/api/docs
    -   **PostgREST (Data API)**: http://localhost/rest/v1/

## Environment Variables
The `docker-compose.local.yml` sets `LOCAL_DEV=true`, which configures the backend to use the local Postgres instance instead of Supabase Cloud.

## Stopping the Stack
To stop the containers:
```bash
docker-compose -f docker-compose.local.yml down
```
To reset the database (delete data):
```bash
docker-compose -f docker-compose.local.yml down -v
```
