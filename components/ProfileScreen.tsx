import React, { useEffect, useState } from 'react';
import { View, Text, ScrollView, TouchableOpacity, TextInput, Alert } from 'react-native';
import { getSupabaseClient, isSupabaseConfigured } from '@/app/lib/supabase';

export function ProfileScreen() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [user, setUser] = useState<{ email?: string } | null>(null);
  const [savedBills, setSavedBills] = useState<{ bill_key: string; actual_bill_number: string | null }[]>([]);
  const [savedLegislators, setSavedLegislators] = useState<{ roster_key: number; first_name: string; last_name: string }[]>([]);
  const [savedError, setSavedError] = useState<string | null>(null);

  useEffect(() => {
    if (!isSupabaseConfigured()) {
      return;
    }

    const supabase = getSupabaseClient();
    if (!supabase) {
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

  useEffect(() => {
    const loadSavedItems = async () => {
      if (!isSupabaseConfigured()) {
        return;
      }
      const supabase = getSupabaseClient();
      if (!supabase) {
        return;
      }
      setSavedError(null);
      const { data: authData } = await supabase.auth.getUser();
      const currentUser = authData.user;
      if (!currentUser) {
        return;
      }
      const [savedBillsRes, savedLegislatorsRes] = await Promise.all([
        supabase
          .from('user_saved_bills')
          .select('bill_key, bills(actual_bill_number)')
          .eq('user_id', currentUser.id),
        supabase
          .from('user_saved_legislators')
          .select('legislator_roster_key, legislators(first_name, last_name)')
          .eq('user_id', currentUser.id),
      ]);

      if (savedBillsRes.error || savedLegislatorsRes.error) {
        setSavedError('Unable to load saved items.');
        return;
      }

      setSavedBills(
        (savedBillsRes.data || []).map((row: any) => ({
          bill_key: row.bill_key,
          actual_bill_number: row.bills?.actual_bill_number ?? null,
        }))
      );
      setSavedLegislators(
        (savedLegislatorsRes.data || []).map((row: any) => ({
          roster_key: row.legislator_roster_key,
          first_name: row.legislators?.first_name ?? '',
          last_name: row.legislators?.last_name ?? '',
        }))
      );
    };

    loadSavedItems();
  }, [user]);

  const signUp = async () => {
    if (!email || !password) {
      Alert.alert('Error', 'Please fill in all fields');
      return;
    }

    if (!isSupabaseConfigured()) {
      Alert.alert('Error', 'Supabase is not configured. Please set your environment variables.');
      return;
    }

    const supabase = getSupabaseClient();
    if (!supabase) {
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

    if (!isSupabaseConfigured()) {
      Alert.alert('Error', 'Supabase is not configured. Please set your environment variables.');
      return;
    }

    const supabase = getSupabaseClient();
    if (!supabase) {
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
      if (!isSupabaseConfigured()) {
        Alert.alert('Error', 'Supabase is not configured. Please set your environment variables.');
        return;
      }

      const supabase = getSupabaseClient();
      if (!supabase) {
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
        {!isSupabaseConfigured() && (
          <View style={{ backgroundColor: '#fee2e2', padding: 12, borderRadius: 8, marginBottom: 16 }}>
            <Text style={{ color: '#991b1b', fontSize: 14 }}>
              Supabase is not configured. Use the Supabase Setup screen to connect your project.
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
