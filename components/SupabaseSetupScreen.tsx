import React, { useEffect, useState } from 'react';
import { View, Text, ScrollView, TextInput, TouchableOpacity, Alert, ActivityIndicator } from 'react-native';
import { useSupabase } from '@/app/lib/supabase';

export function SupabaseSetupScreen() {
  const [url, setUrl] = useState('');
  const [key, setKey] = useState('');
  const [loading, setLoading] = useState(false);
  const [initializing, setInitializing] = useState(false);
  const [logs, setLogs] = useState<string[]>([]);
  const { saveConfig, clearConfig, getConfig, isConfigured } = useSupabase();
  const backendUrl = process.env.EXPO_PUBLIC_BACKEND_API_URL || 'http://localhost:8000';

  useEffect(() => {
    const currentConfig = getConfig();
    if (currentConfig.url) {
      setUrl(currentConfig.url);
    }
    if (currentConfig.key) {
      setKey(currentConfig.key);
    }
  }, [getConfig]);

  const addLog = (msg: string) => {
    setLogs((prev) => [...prev, `${new Date().toLocaleTimeString()}: ${msg}`]);
  };

  const handleSave = async () => {
    if (!url || !key) {
      Alert.alert('Missing fields', 'Please enter both the Supabase URL and key.');
      return;
    }

    setLoading(true);
    try {
      await saveConfig(url, key);
      Alert.alert('Saved', 'Supabase configuration saved successfully.');
    } catch (error) {
      console.error('Supabase config error:', error);
      Alert.alert('Error', 'Unable to save Supabase configuration.');
    } finally {
      setLoading(false);
    }
  };

  const handleClear = async () => {
    setLoading(true);
    try {
      await clearConfig();
      setUrl('');
      setKey('');
      setLogs([]);
      Alert.alert('Cleared', 'Supabase configuration removed.');
    } catch (error) {
      console.error('Supabase clear error:', error);
      Alert.alert('Error', 'Unable to clear Supabase configuration.');
    } finally {
      setLoading(false);
    }
  };

  const handleInitialize = async () => {
    if (!isConfigured) {
      Alert.alert('Configuration Required', 'Please save your Supabase URL and key first.');
      return;
    }

    setInitializing(true);
    setLogs([]);
    addLog('Starting database initialization...');

    try {
      addLog(`Calling backend init endpoint at ${backendUrl}/init...`);
      const response = await fetch(`${backendUrl}/init`, { method: 'POST' });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to initialize database');
      }

      addLog('Database schema initialized successfully.');
      Alert.alert('Success', 'Database initialized successfully. You can now use the app.');


    } catch (err: any) {
      console.error('Error initializing database:', err);
      if (err.message === 'Failed to fetch' || err.message.includes('Network Error')) {
        const errorMsg = `Network Error: Could not reach backend at ${backendUrl}. Ensure the Python backend is running (e.g., uvicorn backend.api:app --reload) and EXPO_PUBLIC_BACKEND_API_URL is set correctly (use your local IP instead of localhost on physical devices).`;
        addLog(errorMsg);
        Alert.alert('Backend Unreachable', errorMsg);
      } else {
        addLog(`Error: ${err.message || 'Failed to initialize database.'}`);
        Alert.alert('Error', 'Failed to initialize database. Check logs for details.');
      }
    } finally {


      setInitializing(false);
    }
  };

  return (
    <ScrollView style={{ flex: 1, backgroundColor: '#f8fafc' }}>
      <View style={{ backgroundColor: '#0f172a', padding: 20 }}>
        <Text style={{ color: '#ffffff', fontSize: 24, fontWeight: 'bold' }}>Setup Required</Text>
      </View>
      <View style={{ padding: 20 }}>
        {!isConfigured && (
          <View style={{ backgroundColor: '#fef3c7', padding: 16, borderRadius: 8, marginBottom: 20 }}>
            <Text style={{ color: '#92400e', fontWeight: '600' }}>No Database Detected</Text>
            <Text style={{ color: '#92400e', marginTop: 4 }}>
              Please configure your database connection and run the initialization script to continue.
            </Text>
          </View>
        )}

        <Text style={{ color: '#475569', marginBottom: 12 }}>
          Enter your Supabase project URL and publishable API key to connect the app.
        </Text>

        <TextInput
          style={{
            borderWidth: 1,
            borderColor: '#e2e8f0',
            borderRadius: 8,
            padding: 12,
            marginBottom: 16,
            backgroundColor: '#ffffff',
          }}
          placeholder="Supabase URL"
          autoCapitalize="none"
          value={url}
          onChangeText={setUrl}
        />
        <TextInput
          style={{
            borderWidth: 1,
            borderColor: '#e2e8f0',
            borderRadius: 8,
            padding: 12,
            marginBottom: 20,
            backgroundColor: '#ffffff',
          }}
          placeholder="Supabase publishable key"
          autoCapitalize="none"
          value={key}
          onChangeText={setKey}
        />

        <View style={{ flexDirection: 'row', gap: 10, marginBottom: 20 }}>
          <TouchableOpacity
            style={{
              backgroundColor: '#059669',
              padding: 14,
              borderRadius: 8,
              alignItems: 'center',
              flex: 1,
            }}
            onPress={handleSave}
            disabled={loading}
          >
            <Text style={{ color: '#ffffff', fontWeight: '600' }}>
              {loading ? 'Saving...' : 'Save Config'}
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={{
              backgroundColor: '#dc2626',
              padding: 14,
              borderRadius: 8,
              alignItems: 'center',
              flex: 1,
            }}
            onPress={handleClear}
            disabled={loading}
          >
            <Text style={{ color: '#ffffff', fontWeight: '600' }}>
              Clear Config
            </Text>
          </TouchableOpacity>
        </View>


        {isConfigured && (
          <View style={{ marginTop: 20, borderTopWidth: 1, borderTopColor: '#e2e8f0', paddingTop: 20 }}>
            <Text style={{ fontSize: 18, fontWeight: 'bold', color: '#1e293b', marginBottom: 12 }}>
              Run a Local Instance
            </Text>
            <Text style={{ color: '#475569', marginBottom: 16 }}>
              If you don't have a backend running, you can launch a local Docker container to fulfill the necessary backend requirements. Run the following command in your terminal from the project root:
            </Text>

            <View style={{ backgroundColor: '#1e293b', borderRadius: 8, padding: 16, marginBottom: 20 }}>
              <Text style={{ color: '#34d399', fontFamily: 'monospace', fontSize: 12 }}>
                docker-compose -f docker-compose.local.yml up -d --build
              </Text>
            </View>

            <Text style={{ fontSize: 18, fontWeight: 'bold', color: '#1e293b', marginBottom: 12 }}>
              Database Initialization
            </Text>

            <Text style={{ color: '#475569', marginBottom: 16 }}>
              Run the setup script to initialize the database schema and prepare the application for data synchronization.
            </Text>

            <TouchableOpacity
              style={{
                backgroundColor: '#3b82f6',
                padding: 14,
                borderRadius: 8,
                alignItems: 'center',
                flexDirection: 'row',
                justifyContent: 'center',
                opacity: initializing ? 0.7 : 1,
              }}
              onPress={handleInitialize}
              disabled={initializing}
            >
              {initializing ? (
                <>
                  <ActivityIndicator color="#ffffff" style={{ marginRight: 8 }} />
                  <Text style={{ color: '#ffffff', fontWeight: '600' }}>Initializing...</Text>
                </>
              ) : (
                <Text style={{ color: '#ffffff', fontWeight: '600' }}>Run Setup Script</Text>
              )}
            </TouchableOpacity>

            {(logs.length > 0 || initializing) && (
              <View style={{ marginTop: 20, backgroundColor: '#1e293b', borderRadius: 8, padding: 16, minHeight: 150 }}>
                <Text style={{ color: '#94a3b8', fontSize: 12, marginBottom: 8, fontWeight: 'bold' }}>SETUP LOGS</Text>
                {logs.map((log, index) => (
                  <Text key={index} style={{ color: '#34d399', fontFamily: 'monospace', fontSize: 12, marginBottom: 4 }}>
                    {log}
                  </Text>
                ))}
              </View>
            )}
          </View>
        )}
      </View>
    </ScrollView>
  );
}

export default SupabaseSetupScreen;
