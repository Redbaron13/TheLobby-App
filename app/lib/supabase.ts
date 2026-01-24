import { createClient, SupabaseClient } from '@supabase/supabase-js';
import AsyncStorage from '@react-native-async-storage/async-storage';

const SUPABASE_URL_KEY = 'supabase_url';
const SUPABASE_KEY_KEY = 'supabase_key';

let supabaseClient: SupabaseClient | null = null;
let supabaseUrl = process.env.EXPO_PUBLIC_SUPABASE_URL ?? '';
let supabaseKey = process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY ?? '';

const buildClient = (url: string, key: string) => createClient(url, key);

export const isSupabaseConfigured = () => Boolean(supabaseUrl && supabaseKey);

export const getSupabaseClient = () => {
  if (supabaseClient || !isSupabaseConfigured()) {
    return supabaseClient;
  }
  supabaseClient = buildClient(supabaseUrl, supabaseKey);
  return supabaseClient;
};

export const loadSupabaseConfig = async () => {
  const [storedUrl, storedKey] = await Promise.all([
    AsyncStorage.getItem(SUPABASE_URL_KEY),
    AsyncStorage.getItem(SUPABASE_KEY_KEY),
  ]);

  if (storedUrl && storedKey) {
    supabaseUrl = storedUrl;
    supabaseKey = storedKey;
    supabaseClient = buildClient(supabaseUrl, supabaseKey);
  }
};

export const saveSupabaseConfig = async (url: string, key: string) => {
  supabaseUrl = url.trim();
  supabaseKey = key.trim();
  await Promise.all([
    AsyncStorage.setItem(SUPABASE_URL_KEY, supabaseUrl),
    AsyncStorage.setItem(SUPABASE_KEY_KEY, supabaseKey),
  ]);
  supabaseClient = buildClient(supabaseUrl, supabaseKey);
  return supabaseClient;
};

export const getSupabaseConfig = () => ({
  url: supabaseUrl,
  key: supabaseKey,
});

export const clearSupabaseConfig = async () => {
  supabaseUrl = '';
  supabaseKey = '';
  supabaseClient = null;
  await Promise.all([
    AsyncStorage.removeItem(SUPABASE_URL_KEY),
    AsyncStorage.removeItem(SUPABASE_KEY_KEY),
  ]);
};
