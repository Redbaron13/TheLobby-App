import React, { useEffect, useState } from 'react';
import { View, Text, ScrollView, TextInput, TouchableOpacity, Alert } from 'react-native';
import { useSupabase } from '@/app/lib/supabase.tsx';

export function SupabaseSetupScreen() {
  const [url, setUrl] = useState('');
  const [key, setKey] = useState('');
  const [loading, setLoading] = useState(false);
  const { saveConfig, clearConfig, getConfig } = useSupabase();

  useEffect(() => {
    const currentConfig = getConfig();
    if (currentConfig.url) {
      setUrl(currentConfig.url);
    }
    if (currentConfig.key) {
      setKey(currentConfig.key);
    }
  }, [getConfig]);

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
      Alert.alert('Cleared', 'Supabase configuration removed.');
    } catch (error) {
      console.error('Supabase clear error:', error);
      Alert.alert('Error', 'Unable to clear Supabase configuration.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView style={{ flex: 1, backgroundColor: '#f8fafc' }}>
      <View style={{ backgroundColor: '#0f172a', padding: 20 }}>
        <Text style={{ color: '#ffffff', fontSize: 24, fontWeight: 'bold' }}>Supabase Setup</Text>
      </View>
      <View style={{ padding: 20 }}>
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

        <TouchableOpacity
          style={{
            backgroundColor: '#059669',
            padding: 14,
            borderRadius: 8,
            alignItems: 'center',
            marginBottom: 12,
          }}
          onPress={handleSave}
          disabled={loading}
        >
          <Text style={{ color: '#ffffff', fontWeight: '600' }}>
            {loading ? 'Saving...' : 'Save Configuration'}
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={{
            backgroundColor: '#dc2626',
            padding: 14,
            borderRadius: 8,
            alignItems: 'center',
          }}
          onPress={handleClear}
          disabled={loading}
        >
          <Text style={{ color: '#ffffff', fontWeight: '600' }}>
            Clear Configuration
          </Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}

export default SupabaseSetupScreen;
