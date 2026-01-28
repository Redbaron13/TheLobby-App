# Supabase Admin Environment Configuration Template
# Copy this file to .env and fill in your actual values

################################################################################
# SUPABASE PROJECT DETAILS
################################################################################

SUPABASE_PROJECT_ID="your-supabase-project-id"
SUPABASE_URL="https://your-project-id.supabase.co"

################################################################################
# API KEYS - SECURITY WARNING
################################################################################

# NEVER commit actual keys to git. Use environment variables in production.

# Service Role Key - FOR SERVER USE ONLY
# Has full admin access. DO NOT expose this to the client.
SUPABASE_SERVICE_ROLE_KEY="your-service-role-key"

# Publishable Key - Safe to share
# Can be used in client-side code
SUPABASE_PUBLISHABLE_KEY="your-publishable-key"

# Optional: Anonymous Key (old naming convention)
SUPABASE_ANON_KEY="your-anon-key"
