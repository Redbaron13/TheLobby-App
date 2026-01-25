import { createClient, SupabaseClient } from '@supabase/supabase-js';
import AsyncStorage from '@react-native-async-storage/async-storage';

type SupabaseConfig = {
  url: string;
  key: string;
};

const STORAGE_KEY = 'supabase_config';
const envConfig: SupabaseConfig = {
  url: process.env.SUPABASE_URL ?? '',
  key: process.env.SUPABASE_ANON_KEY ?? '',
};

let cachedConfig: SupabaseConfig = { ...envConfig };
let cachedClient: SupabaseClient | null = envConfig.url && envConfig.key
  ? createClient(envConfig.url, envConfig.key)
  : null;

const setConfig = (config: SupabaseConfig) => {
  cachedConfig = { ...config };
  cachedClient = isSupabaseConfigured()
    ? createClient(cachedConfig.url, cachedConfig.key)
    : null;
};

export const isSupabaseConfigured = () => Boolean(cachedConfig.url && cachedConfig.key);

export const getSupabaseClient = () => cachedClient;

export const getSupabaseConfig = () => ({ ...cachedConfig });

export const loadSupabaseConfig = async () => {
  try {
    const stored = await AsyncStorage.getItem(STORAGE_KEY);
    if (!stored) {
      return;
    }
    const parsed = JSON.parse(stored) as SupabaseConfig;
    if (parsed?.url && parsed?.key) {
      setConfig(parsed);
    }
  } catch (error) {
    console.warn('Unable to load Supabase config from storage.', error);
  }
};

export const saveSupabaseConfig = async (url: string, key: string) => {
  const config: SupabaseConfig = { url, key };
  setConfig(config);
  await AsyncStorage.setItem(STORAGE_KEY, JSON.stringify(config));
};

export const clearSupabaseConfig = async () => {
  await AsyncStorage.removeItem(STORAGE_KEY);
  setConfig(envConfig);
};
