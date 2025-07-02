import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView, TouchableOpacity } from 'react-native';
import { supabase } from '@/app/lib/supabase';
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

export function SenateScreen() {
  const [senators, setSenators] = useState<Legislator[]>([]);
  const [recentBills, setRecentBills] = useState<Bill[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSenateData();
  }, []);

  const getFullName = (legislator: Legislator) => {
    const parts = [legislator.Firstname, legislator.MidName, legislator.LastName, legislator.Suffix].filter(Boolean);
    return parts.join(' ');
  };

  const loadSenateData = async () => {
    try {
      const [senatorsRes, billsRes] = await Promise.all([
        supabase.from('legislators').select('*').eq('House', 'Senate').order('LastName'),
        supabase.from('bills').select('*').order('IntroDate', { ascending: false }).limit(5)
      ]);

      if (senatorsRes.error) throw senatorsRes.error;
      if (billsRes.error) throw billsRes.error;

      setSenators(senatorsRes.data || []);
      setRecentBills(billsRes.data || []);
    } catch (error) {
      console.error('Error loading senate data:', error);
    } finally {
      setLoading(false);
    }
  };

  const leadership = senators.filter(s => s.LegPos && s.LegPos.toLowerCase().includes('president'));
  const democrats = senators.filter(s => s.Party?.toLowerCase().includes('democrat')).length;
  const republicans = senators.filter(s => s.Party?.toLowerCase().includes('republican')).length;

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
      </View>
    </ScrollView>
  );
}

export default SenateScreen;