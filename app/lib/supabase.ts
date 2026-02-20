import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { createClient, SupabaseClient } from '@supabase/supabase-js';
import AsyncStorage from '@react-native-async-storage/async-storage';
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

// Helper to check env vars
const getEnvConfig = () => {
  const url = process.env.EXPO_PUBLIC_SUPABASE_URL;
  const key = process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY;
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
      // Try AsyncStorage first
      const storedUrl = await AsyncStorage.getItem('supabase_url');
      const storedKey = await AsyncStorage.getItem('supabase_key');

      if (storedUrl && storedKey) {
        initializeClient(storedUrl, storedKey);
      } else {
        // Fallback to Env Vars
        const { url, key } = getEnvConfig();
        if (url && key) {
          initializeClient(url, key);
        }
      }
    } catch (e) {
      console.error('Failed to load Supabase config', e);
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

    // Check env vars again? Maybe, but usually clear implies "I want to logout/reset".
    // If env vars exist, it might re-login on next reload.
    // For now, let's just clear.
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

// Re-export for backward compatibility (but deprecated)
// To make migration easier, we can't really export a hook result as a constant.
// So we will remove the old exports and fix the callers.

// Helper functions for direct usage if needed (e.g. outside React tree - discouraged)
export const getSupabaseConfig = () => {
   // This is synchronous and can't read AsyncStorage easily without async.
   // But the previous code had it synchronous? No, previous code had `loadSupabaseConfig` as async.
   // Components/SupabaseSetupScreen used `getSupabaseConfig` synchronously in useEffect?
   // Let's check SupabaseSetupScreen usage.
   return { url: '', key: '' }; // Placeholder, consumers should use hook
};
