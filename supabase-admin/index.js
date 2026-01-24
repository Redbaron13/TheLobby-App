const dotenv = require("dotenv");
const { createClient } = require("@supabase/supabase-js");

dotenv.config();

const { SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY } = process.env;

if (!SUPABASE_URL || !SUPABASE_SERVICE_ROLE_KEY) {
  throw new Error(
    "Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY. Load them from your .env file."
  );
}

// Service role keys must never be exposed to client code or prompts.
const supabaseAdmin = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY);

async function listUsers() {
  const { data, error } = await supabaseAdmin.from("users").select("*");
  if (error) {
    throw new Error(`Failed to fetch users: ${error.message}`);
  }
  return data ?? [];
}

module.exports = {
  supabaseAdmin,
  listUsers,
};

if (require.main === module) {
  listUsers()
    .then((rows) => {
      console.log("Users:", rows);
    })
    .catch((err) => {
      console.error("Error listing users:", err.message);
      process.exitCode = 1;
    });
}
