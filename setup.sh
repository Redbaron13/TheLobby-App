#!/bin/bash

# TheLobby-App Setup Script
# This script initializes the repository for local development and Docker usage.

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}======================================"
echo -e "      TheLobby-App Setup Script"
echo -e "======================================"
echo -e "${NC}"

# Function to check if a command exists
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${RED}Error: $1 is not installed.${NC}"
        return 1
    fi
    return 0
}

# 1. Dependency Checks
echo -e "${YELLOW}1. Checking dependencies...${NC}"
check_command "node"
check_command "npm"
check_command "python3"
check_command "docker"
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}Error: docker-compose is not installed.${NC}"
    exit 1
fi

# 2. Environment Variables Setup
echo -e "\n${YELLOW}2. Setting up environment variables...${NC}"
if [ ! -f ".env.local" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env.local
        echo -e "${GREEN}Created .env.local from .env.example${NC}"
    else
        echo -e "${RED}.env.example not found!${NC}"
    fi
else
    echo -e "✔ .env.local already exists"
fi

if [ ! -f "backend/.env" ]; then
    if [ -f "backend/.env.example" ]; then
        cp backend/.env.example backend/.env
        echo -e "${GREEN}Created backend/.env from backend/.env.example${NC}"
    else
        echo -e "${RED}backend/.env.example not found!${NC}"
    fi
else
    echo -e "✔ backend/.env already exists"
fi

# 3. Install Frontend Dependencies
echo -e "\n${YELLOW}3. Installing frontend dependencies...${NC}"
npm install
echo -e "${GREEN}✔ Frontend dependencies installed${NC}"

# 4. Install Backend Dependencies
echo -e "\n${YELLOW}4. Installing backend dependencies...${NC}"
python3 -m pip install -r backend/requirements.txt
echo -e "${GREEN}✔ Backend dependencies installed${NC}"

# 5. Database Initialization (Optional)
echo -e "\n${YELLOW}5. Database Initialization${NC}"
read -p "Do you want to initialize the Supabase database schema now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Initializing database..."
    # Check if SUPABASE_DB_URL is set in backend/.env
    if grep -q "SUPABASE_DB_URL=your-" "backend/.env"; then
        echo -e "${RED}Error: SUPABASE_DB_URL is not configured in backend/.env. Please edit it first.${NC}"
    else
        PYTHONPATH=. python3 backend/init_supabase.py
        echo -e "${GREEN}✔ Database initialized${NC}"
    fi
fi

# 6. Verification
echo -e "\n${YELLOW}6. Verifying setup...${NC}"
bash scripts/validate-env.sh

echo -e "\n${GREEN}======================================"
echo -e "           Setup Complete!"
echo -e "======================================"
echo -e "${NC}"
echo -e "To run the app locally:"
echo -e "  Backend: PYTHONPATH=. uvicorn backend.api:app --reload"
echo -e "  Frontend: npx expo start --web"
echo -e ""
echo -e "To run using Docker:"
echo -e "  docker-compose up --build"
echo -e ""
echo -e "Visit the Admin Dashboard at /admin to manage data sync."
