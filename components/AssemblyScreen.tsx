import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView, TouchableOpacity, ActivityIndicator } from 'react-native';
import { supabase, isSupabaseConfigured } from '@/app/lib/supabase';
import { ChamberVisualization } from './ChamberVisualization';
import { styles } from './LegislatorsScreenStyles';

interface Legislator {
  id: number;
  Firstname: string;
  LastName: string;
  MidName?: string;
  Suffix?: string;
  Party: string;
  House: string;
  District: string;
  LegPos?: string;
}

interface Bill {
  id: number;
  ActualBillNumber: string;
  Synopsis: string;
  CurrentStatus: string;
  IntroDate: string;
}

export function AssemblyScreen() {
  const [assemblyMembers, setAssemblyMembers] = useState<Legislator[]>([]);
  const [recentBills, setRecentBills] = useState<Bill[]>([]);
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    loadAssemblyData();
  }, []);

  const getFullName = (legislator: Legislator) => {
    const parts = [legislator.Firstname, legislator.MidName, legislator.LastName, legislator.Suffix].filter(Boolean);
    return parts.join(' ');
  };

  const loadAssemblyData = async () => {
    if (!isSupabaseConfigured || !supabase) {
      setErrorMessage('Supabase is not configured. Set EXPO_PUBLIC_SUPABASE_URL and EXPO_PUBLIC_SUPABASE_ANON_KEY.');
      setLoading(false);
      return;
    }

    try {
      const [assemblyRes, billsRes] = await Promise.all([
        supabase.from('legislators').select('*').eq('House', 'Assembly').order('LastName'),
        supabase.from('bills').select('*').order('IntroDate', { ascending: false }).limit(5)
      ]);
      
      if (assemblyRes.error) throw assemblyRes.error;
      if (billsRes.error) throw billsRes.error;
      
      setAssemblyMembers(assemblyRes.data || []);
      setRecentBills(billsRes.data || []);
    } catch (error) {
      console.error('Error loading assembly data:', error);
      setErrorMessage('Unable to load assembly data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const leadership = assemblyMembers.filter(m => m.LegPos && m.LegPos.toLowerCase().includes('speaker'));
  const democrats = assemblyMembers.filter(m => m.Party?.toLowerCase().includes('democrat')).length;
  const republicans = assemblyMembers.filter(m => m.Party?.toLowerCase().includes('republican')).length;

  const committees = [
    'Judiciary', 'Budget', 'Environment & Solid Waste',
    'Health', 'Transportation & Independent Authorities',
    'Education', 'Commerce & Economic Development', 'Labor'
  ];

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>New Jersey General Assembly</Text>
        
        <ChamberVisualization
          chamber="assembly"
          democratCount={democrats}
          republicanCount={republicans}
          totalSeats={80}
        />
      </View>
      
      <View style={styles.content}>
        {loading ? (
          <ActivityIndicator size="large" color="#0f172a" style={{ marginTop: 24 }} />
        ) : errorMessage ? (
          <Text style={styles.noDataText}>{errorMessage}</Text>
        ) : (
          <>
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Assembly Leadership</Text>
              {leadership.map(leader => (
                <View key={leader.id} style={styles.legislatorCard}>
                  <Text style={styles.legislatorName}>{getFullName(leader)}</Text>
                  <Text style={styles.leadershipPosition}>{leader.LegPos}</Text>
                  <Text style={styles.legislatorInfo}>District {leader.District} - {leader.Party}</Text>
                </View>
              ))}
            </View>

            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Recent Bills</Text>
              {recentBills.map(bill => (
                <TouchableOpacity key={bill.id} style={styles.legislatorCard}>
                  <Text style={styles.legislatorName}>{bill.ActualBillNumber}</Text>
                  <Text style={styles.legislatorInfo}>{bill.Synopsis}</Text>
                  <Text style={styles.committees}>Status: {bill.CurrentStatus}</Text>
                </TouchableOpacity>
              ))}
            </View>

            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Assembly Committees</Text>
              {committees.map(committee => (
                <TouchableOpacity key={committee} style={styles.legislatorCard}>
                  <Text style={styles.legislatorName}>{committee}</Text>
                  <Text style={styles.legislatorInfo}>View committee details and upcoming schedule</Text>
                </TouchableOpacity>
              ))}
            </View>
          </>
        )}
      </View>
    </ScrollView>
  );
}

export default AssemblyScreen;
