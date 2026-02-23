#!/bin/bash

################################################################################
# ENVIRONMENT VALIDATION SCRIPT
# Checks that all required environment variables are configured correctly
################################################################################

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "================================"
echo "TheLobby-App Environment Checker"
echo "================================"
echo ""

# Check frontend environment
echo "📱 FRONTEND (.env.local or .env.example):"
check_var() {
    if [ -z "${!1}" ]; then
        echo -e "  ${RED}✗${NC} $1 is not set"
        return 1
    else
        echo -e "  ${GREEN}✓${NC} $1 is set"
        return 0
    fi
}

# Try to load .env files
if [ -f "$PROJECT_ROOT/.env.local" ]; then
    set -a
    . "$PROJECT_ROOT/.env.local"
    set +a
    echo "Loaded .env.local"
fi

if [ -f "$PROJECT_ROOT/.env.example" ]; then
    set -a
    . "$PROJECT_ROOT/.env.example"
    set +a
    echo "Loaded .env.example as fallback"
fi

echo ""
echo "Checking Frontend Variables:"
FRONTEND_OK=true
check_var "EXPO_PUBLIC_SUPABASE_URL" || FRONTEND_OK=false
check_var "EXPO_PUBLIC_SUPABASE_ANON_KEY" || FRONTEND_OK=false
check_var "EXPO_PUBLIC_BACKEND_API_URL" || FRONTEND_OK=false

# Check backend environment
echo ""
echo "🐍 BACKEND (.env or .env.example):"
if [ -f "$PROJECT_ROOT/backend/.env" ]; then
    set -a
    . "$PROJECT_ROOT/backend/.env"
    set +a
    echo "Loaded backend/.env"
fi

if [ -f "$PROJECT_ROOT/backend/.env.example" ]; then
    set -a
    . "$PROJECT_ROOT/backend/.env.example"
    set +a
    echo "Loaded backend/.env.example as fallback"
fi

echo ""
echo "Checking Backend Variables:"
BACKEND_OK=true
check_var "SUPABASE_URL" || BACKEND_OK=false
check_var "SUPABASE_SERVICE_ROLE_KEY" || BACKEND_OK=false
check_var "NJLEG_DOWNLOAD_BASE_URL" || BACKEND_OK=false
check_var "NJLEG_DATA_DIR" || BACKEND_OK=false
check_var "DATA_RETENTION_DAYS" || BACKEND_OK=false

# Check admin tools environment
echo ""
echo "🛠️  ADMIN TOOLS (supabase-admin/.env or example-env.md):"
if [ -f "$PROJECT_ROOT/supabase-admin/.env" ]; then
    set -a
    . "$PROJECT_ROOT/supabase-admin/.env"
    set +a
    echo "Loaded supabase-admin/.env"
fi

echo ""
echo "Checking Admin Variables:"
ADMIN_OK=true
check_var "SUPABASE_PROJECT_ID" || ADMIN_OK=false
check_var "SUPABASE_URL" || ADMIN_OK=false
check_var "SUPABASE_SERVICE_ROLE_KEY" || ADMIN_OK=false

# Validate consistency
echo ""
echo "🔍 CONSISTENCY CHECKS:"
if [ ! -z "$SUPABASE_URL" ] && [ ! -z "$EXPO_PUBLIC_SUPABASE_URL" ]; then
    if [ "$SUPABASE_URL" == "$EXPO_PUBLIC_SUPABASE_URL" ]; then
        echo -e "  ${GREEN}✓${NC} SUPABASE_URL is consistent"
    else
        echo -e "  ${RED}✗${NC} SUPABASE_URL mismatch!"
        echo "    Backend: $SUPABASE_URL"
        echo "    Frontend: $EXPO_PUBLIC_SUPABASE_URL"
        FRONTEND_OK=false
        BACKEND_OK=false
    fi
fi

# Final report
echo ""
echo "================================"
echo "SUMMARY:"
echo "================================"
echo ""

if [ "$FRONTEND_OK" = true ]; then
    echo -e "${GREEN}✓ Frontend${NC} - All required variables set"
else
    echo -e "${RED}✗ Frontend${NC} - Missing required variables"
fi

if [ "$BACKEND_OK" = true ]; then
    echo -e "${GREEN}✓ Backend${NC} - All required variables set"
else
    echo -e "${RED}✗ Backend${NC} - Missing required variables"
fi

if [ "$ADMIN_OK" = true ]; then
    echo -e "${GREEN}✓ Admin Tools${NC} - All required variables set"
else
    echo -e "${RED}✗ Admin Tools${NC} - Missing required variables"
fi

echo ""
if [ "$FRONTEND_OK" = true ] && [ "$BACKEND_OK" = true ] && [ "$ADMIN_OK" = true ]; then
    echo -e "${GREEN}✅ All checks passed!${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠️  Some checks failed. See above for details.${NC}"
    echo ""
    echo "Setup instructions:"
    echo "  1. Copy template files: cp .env.example .env.local (frontend)"
    echo "  2. Copy template files: cp backend/.env.example backend/.env"
    echo "  3. Edit .env files with your actual credentials"
    echo "  4. Run this script again to verify"
    exit 1
fi
