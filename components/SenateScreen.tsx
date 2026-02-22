import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView, TouchableOpacity, ActivityIndicator } from 'react-native';
import { useSupabase } from '@/app/lib/supabase.tsx';
import { ChamberVisualization } from './ChamberVisualization';
import { styles } from './LegislatorsScreenStyles';

interface Legislator {
  roster_key: number;
  first_name: string;
  last_name: string;
  mid_name?: string;
  suffix?: string;
  party: string;
  house: string;
  district: string;
  leg_pos?: string;
  leg_status?: string;
}

interface Bill {
  bill_key: string;
  actual_bill_number: string;
  synopsis: string;
  current_status: string;
  intro_date: string;
}

export function SenateScreen() {
  const { supabase, isConfigured } = useSupabase();
  const [senators, setSenators] = useState<Legislator[]>([]);
  const [recentBills, setRecentBills] = useState<Bill[]>([]);
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    loadSenateData();
  }, [supabase, isConfigured]);

  const getFullName = (legislator: Legislator) => {
    const parts = [legislator.first_name, legislator.mid_name, legislator.last_name, legislator.suffix].filter(Boolean);
    return parts.join(' ');
  };

  const loadSenateData = async () => {
    if (!isConfigured || !supabase) {
      setErrorMessage('Supabase is not configured. Go to the Setup screen to configure it.');
      setLoading(false);
      return;
    }

    try {
      const [senatorsRes, billsRes] = await Promise.all([
        supabase.from('legislators').select('*').eq('house', 'Senate').order('last_name'),
        supabase.from('bills').select('*').order('intro_date', { ascending: false }).limit(5)
      ]);

      if (senatorsRes.error) throw senatorsRes.error;
      if (billsRes.error) throw billsRes.error;

      setSenators(senatorsRes.data || []);
      setRecentBills(billsRes.data || []);
    } catch (error) {
      console.error('Error loading senate data:', error);
      setErrorMessage('Unable to load senate data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const leadership = senators.filter(s => s.leg_pos && s.leg_pos.toLowerCase().includes('president'));
  const democrats = senators.filter(s => s.party?.toLowerCase().includes('democrat')).length;
  const republicans = senators.filter(s => s.party?.toLowerCase().includes('republican')).length;

  const committees = [
    'Judiciary', 'Budget & Appropriations', 'Environment & Energy',
    'Health, Human Services & Senior Citizens', 'Transportation',
    'Education', 'Commerce', 'Labor'
  ];

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>New Jersey Senate</Text>

        <ChamberVisualization
          chamber="senate"
          democratCount={democrats}
          republicanCount={republicans}
          totalSeats={40}
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
              <Text style={styles.sectionTitle}>Senate Leadership</Text>
              {leadership.map(leader => (
                <View key={`leader-${leader.id}`} style={styles.legislatorCard}>
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
              <Text style={styles.sectionTitle}>Senate Committees</Text>
              {committees.map(committee => (
                <TouchableOpacity key={committee} style={styles.legislatorCard}>
                  <Text style={styles.legislatorName}>{committee}</Text>
                  <Text style={styles.legislatorInfo}>View committee details and upcoming schedule</Text>
                </TouchableOpacity>
              ))}
            </View>

            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Senators</Text>
              {senators.map((legislator) => (
                <View key={`senator-${legislator.id}`} style={styles.legislatorCard}>
                  <Text style={styles.legislatorName}>{getFullName(legislator)}</Text>
                  <Text style={styles.legislatorInfo}>District {legislator.District} - {legislator.Party}</Text>
                </View>
              ))}
            </View>
          </>
        )}
      </View>
    </ScrollView>
  );
}

export default SenateScreen;
