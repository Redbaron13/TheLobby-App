import React, { useEffect, useState } from 'react';
import { View, Text, ScrollView, TouchableOpacity, TextInput, Alert } from 'react-native';
import { useSupabase } from '@/app/lib/supabase';

export function ProfileScreen() {
  const { supabase, isConfigured } = useSupabase();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [user, setUser] = useState<{ email?: string } | null>(null);

  useEffect(() => {
    if (!isConfigured || !supabase) {
      return;
    }

    supabase.auth.getSession().then(({ data }) => {
      setUser(data.session?.user ?? null);
    });

    const { data: authListener } = supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user ?? null);
    });

    return () => {
      authListener.subscription.unsubscribe();
    };
  }, []);

  const signUp = async () => {
    if (!email || !password) {
      Alert.alert('Error', 'Please fill in all fields');
      return;
    }

    if (!isConfigured || !supabase) {
      Alert.alert('Error', 'Supabase is not configured. Please set your environment variables.');
      return;
    }

    setLoading(true);
    try {
      const { data, error } = await supabase.auth.signUp({
        email: email,
        password: password,
      });

      if (error) throw error;
      Alert.alert('Success', 'Check your email for verification link!');
    } catch (error: any) {
      Alert.alert('Error', error.message);
    } finally {
      setLoading(false);
    }
  };

  const signIn = async () => {
    if (!email || !password) {
      Alert.alert('Error', 'Please fill in all fields');
      return;
    }

    if (!isConfigured || !supabase) {
      Alert.alert('Error', 'Supabase is not configured. Please set your environment variables.');
      return;
    }

    setLoading(true);
    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email: email,
        password: password,
      });

      if (error) throw error;
      setUser(data.user);
      Alert.alert('Success', 'Signed in successfully!');
    } catch (error: any) {
      Alert.alert('Error', error.message);
    } finally {
      setLoading(false);
    }
  };

  const signOut = async () => {
    try {
      if (!isConfigured || !supabase) {
        Alert.alert('Error', 'Supabase is not configured. Please set your environment variables.');
        return;
      }

      await supabase.auth.signOut();
      setUser(null);
      setSavedBills([]);
      setSavedLegislators([]);
      Alert.alert('Success', 'Signed out successfully!');
    } catch (error: any) {
      Alert.alert('Error', error.message);
    }
  };

  return (
    <ScrollView style={{ flex: 1, backgroundColor: '#f8fafc' }}>
      <View style={{ backgroundColor: '#1e40af', padding: 20 }}>
        <Text style={{ fontSize: 28, fontWeight: 'bold', color: '#ffffff' }}>Profile</Text>
      </View>

      <View style={{ padding: 20 }}>
        {!isConfigured && (
          <View style={{ backgroundColor: '#fee2e2', padding: 12, borderRadius: 8, marginBottom: 16 }}>
            <Text style={{ color: '#991b1b', fontSize: 14 }}>
              Supabase is not configured. Add EXPO_PUBLIC_SUPABASE_URL and EXPO_PUBLIC_SUPABASE_ANON_KEY to enable sign in.
            </Text>
          </View>
        )}
        {user ? (
          <View>
            <Text style={{ fontSize: 18, fontWeight: 'bold', color: '#1e40af', marginBottom: 10 }}>
              Welcome, {user.email}!
            </Text>
            <Text style={{ fontSize: 16, color: '#64748b', marginBottom: 20 }}>
              You are signed in to NJ Legislature Tracker
            </Text>

            <TouchableOpacity
              style={{
                backgroundColor: '#dc2626',
                padding: 15,
                borderRadius: 8,
                alignItems: 'center'
              }}
              onPress={signOut}
            >
              <Text style={{ color: '#ffffff', fontSize: 16, fontWeight: 'bold' }}>
                Sign Out
              </Text>
            </TouchableOpacity>
            <View style={{ marginTop: 24 }}>
              <Text style={{ fontSize: 18, fontWeight: 'bold', color: '#1e40af', marginBottom: 10 }}>
                Saved Bills
              </Text>
              {savedError && (
                <Text style={{ color: '#dc2626', marginBottom: 8 }}>{savedError}</Text>
              )}
              {savedBills.length === 0 && (
                <Text style={{ color: '#64748b', marginBottom: 12 }}>No saved bills yet.</Text>
              )}
              {savedBills.map((bill) => (
                <Text key={bill.bill_key} style={{ color: '#475569', marginBottom: 6 }}>
                  {bill.actual_bill_number || bill.bill_key}
                </Text>
              ))}

              <Text style={{ fontSize: 18, fontWeight: 'bold', color: '#1e40af', marginTop: 16, marginBottom: 10 }}>
                Saved Legislators
              </Text>
              {savedLegislators.length === 0 && (
                <Text style={{ color: '#64748b' }}>No saved legislators yet.</Text>
              )}
              {savedLegislators.map((legislator) => (
                <Text key={legislator.roster_key} style={{ color: '#475569', marginBottom: 6 }}>
                  {legislator.first_name} {legislator.last_name}
                </Text>
              ))}
            </View>
          </View>
        ) : (
          <View>
            <Text style={{ fontSize: 18, fontWeight: 'bold', color: '#1e40af', marginBottom: 20 }}>
              Sign In / Sign Up
            </Text>

            <TextInput
              style={{
                borderWidth: 1,
                borderColor: '#d1d5db',
                padding: 12,
                borderRadius: 8,
                marginBottom: 15,
                backgroundColor: '#ffffff'
              }}
              placeholder="Email"
              value={email}
              onChangeText={setEmail}
              keyboardType="email-address"
              autoCapitalize="none"
            />

            <TextInput
              style={{
                borderWidth: 1,
                borderColor: '#d1d5db',
                padding: 12,
                borderRadius: 8,
                marginBottom: 20,
                backgroundColor: '#ffffff'
              }}
              placeholder="Password"
              value={password}
              onChangeText={setPassword}
              secureTextEntry
            />

            <View style={{ flexDirection: 'row', gap: 10 }}>
              <TouchableOpacity
                style={{
                  flex: 1,
                  backgroundColor: '#1e40af',
                  padding: 15,
                  borderRadius: 8,
                  alignItems: 'center'
                }}
                onPress={signIn}
                disabled={loading}
              >
                <Text style={{ color: '#ffffff', fontSize: 16, fontWeight: 'bold' }}>
                  Sign In
                </Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={{
                  flex: 1,
                  backgroundColor: '#d97706',
                  padding: 15,
                  borderRadius: 8,
                  alignItems: 'center'
                }}
                onPress={signUp}
                disabled={loading}
              >
                <Text style={{ color: '#ffffff', fontSize: 16, fontWeight: 'bold' }}>
                  Sign Up
                </Text>
              </TouchableOpacity>
            </View>
          </View>
        )}
      </View>
    </ScrollView>
  );
}

export default ProfileScreen;
