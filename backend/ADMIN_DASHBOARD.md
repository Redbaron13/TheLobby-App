# Admin dashboard design (app-facing)

This document defines the **administrator-only backend interface** that should live in the app’s Admin Profile area. The goal is to let approved administrators **monitor, start/stop, and tune ingestion pipelines** while protecting sensitive data and enforcing strong security controls.

---

## 1) Access control (required)

Only administrators should see or access these screens.

**Recommended approach (Supabase):**
- Use **Auth + RLS**.
- Require a `role=admin` value in `auth.users.app_metadata`.
- Enforce the role in RLS policies for all admin tables.
- Hide admin navigation for non-admin users in the UI.

**Example policy (conceptual):**
```sql
create policy "admins only"
on admin_pipeline_runs
for all
using (auth.jwt() ->> 'role' = 'admin');
```

---

## 2) Admin dashboard pages

### A) Pipeline control & monitoring
**Purpose:** start/stop pipelines, adjust settings, and review logs.

**UI capabilities:**
- Start/Stop legislative ingestion
- Start/Stop GIS ingestion
- View last run status, row counts, validation issues
- Edit settings (download URLs, years, retention)
- Re-run the legislature scraper with updated parameters

**Recommended tables:**
- `admin_pipeline_settings`  
  Store user-tunable settings for each pipeline.
- `admin_pipeline_runs`  
  Store run metadata: start time, end time, status, counts, error messages.
- `admin_pipeline_logs`  
  Store structured log messages.

---

### B) User management & analytics
**Purpose:** reset passwords, verify new users, and analyze usage.

**UI capabilities:**
- Reset user passwords (admin-initiated)
- View new sign-ups and mark verified
- View “most searched legislator” and “most followed bill”
- Review audit trail for admin actions

**Recommended tables:**
- `admin_user_actions`  
  Admin audit log (who did what, when)
- `user_search_analytics`  
  Aggregated search counts
- `user_follow_analytics`  
  Aggregated bill follows

---

## 3) Security best practices

1. **Never store plaintext secrets** in app UI tables.  
   Keep keys in environment variables or Supabase secrets.
2. **Use row-level security (RLS)** on all admin tables.
3. **Require MFA** for admin users where possible.
4. **Log every admin action** with user id + timestamp.
5. **Validate all admin inputs** server-side before applying pipeline changes.

---

## 4) Integration with pipelines

The ingestion pipelines should read **admin_pipeline_settings** at runtime to pick up changes without code edits.
For example:
- Update `NJLEG_BILL_TRACKING_YEARS` from settings table
- Enable/disable GIS ingestion without redeploy
- Override download base URLs for the NJ Legislature scraper

When a pipeline runs, it should:
1. Insert a row into `admin_pipeline_runs` with `status=running`.
2. Log progress into `admin_pipeline_logs`.
3. Update the run row with `status=success|failed`.

---

## 5) Minimum “ready” criteria

To call the admin dashboard **production-ready**:
- All admin endpoints are protected by role-based access.
- Admin changes are validated and logged.
- Pipelines can be started/stopped and settings persist.
- Audit trail is complete and immutable (append-only).
