import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { createClient, SupabaseClient } from '@supabase/supabase-js';
import AsyncStorage from '@react-native-async-storage/async-storage';
import Constants from 'expo-constants';
import 'react-native-url-polyfill/auto';

// Define the shape of our context
interface SupabaseContextType {
  supabase: SupabaseClient | null;
  isConfigured: boolean;
  saveConfig: (url: string, key: string) => Promise<void>;
  clearConfig: () => Promise<void>;
  getConfig: () => { url: string; key: string };
}

const SupabaseContext = createContext<SupabaseContextType | undefined>(undefined);

// Helper to check env vars - support Expo, Next.js, and expo-constants
const getEnvConfig = () => {
  const extra = Constants.expoConfig?.extra;
  const url =
    process.env.EXPO_PUBLIC_SUPABASE_URL ||
    process.env.NEXT_PUBLIC_SUPABASE_URL ||
    extra?.supabaseUrl ||
    '';
  const key =
    process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY ||
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ||
    process.env.SUPABASE_ANON_KEY ||
    extra?.supabaseAnonKey ||
    '';
  return { url, key };
};

export function SupabaseProvider({ children }: { children: ReactNode }) {
  const [client, setClient] = useState<SupabaseClient | null>(null);
  const [config, setConfig] = useState<{ url: string; key: string }>({ url: '', key: '' });
  const [isConfigured, setIsConfigured] = useState(false);

  // Load config on mount
  useEffect(() => {
    loadConfig();
  }, []);

  const loadConfig = async () => {
    try {
      // Try env vars first (most reliable in web/sandbox environments)
      const { url, key } = getEnvConfig();
      if (url && key) {
        initializeClient(url, key);
        return;
      }

      // Fallback to AsyncStorage
      const storedUrl = await AsyncStorage.getItem('supabase_url');
      const storedKey = await AsyncStorage.getItem('supabase_key');

      if (storedUrl && storedKey) {
        initializeClient(storedUrl, storedKey);
      }
    } catch (e) {
      console.error('Failed to load Supabase config', e);
      // Last resort: try env vars even if AsyncStorage failed
      const { url, key } = getEnvConfig();
      if (url && key) {
        initializeClient(url, key);
      }
    }
  };

  const initializeClient = (url: string, key: string) => {
    try {
      const newClient = createClient(url, key, {
        auth: {
          storage: AsyncStorage,
          autoRefreshToken: true,
          persistSession: true,
          detectSessionInUrl: false,
        },
      });
      setClient(newClient);
      setConfig({ url, key });
      setIsConfigured(true);
    } catch (e) {
      console.error('Failed to initialize Supabase client', e);
      setClient(null);
      setIsConfigured(false);
    }
  };

  const saveConfig = async (url: string, key: string) => {
    await AsyncStorage.setItem('supabase_url', url);
    await AsyncStorage.setItem('supabase_key', key);
    initializeClient(url, key);
  };

  const clearConfig = async () => {
    await AsyncStorage.removeItem('supabase_url');
    await AsyncStorage.removeItem('supabase_key');
    setClient(null);
    setConfig({ url: '', key: '' });
    setIsConfigured(false);
  };

  const getConfig = () => config;

  return (
    <SupabaseContext.Provider value={{ supabase: client, isConfigured, saveConfig, clearConfig, getConfig }}>
      {children}
    </SupabaseContext.Provider>
);
}
export function useSupabase() {
  const context = useContext(SupabaseContext);
  if (context === undefined) {
    throw new Error('useSupabase must be used within a SupabaseProvider');
  }
  return context;
}
