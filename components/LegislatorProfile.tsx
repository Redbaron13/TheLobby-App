import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity } from 'react-native';
import { getSupabaseClient, isSupabaseConfigured } from '@/app/lib/supabase';

interface Legislator {
  roster_key: number;
  first_name: string;
  last_name: string;
  mid_name?: string;
  suffix?: string;
  party: string;
  house: string;
  district: number;
  title?: string;
  leg_pos?: string;
  email?: string;
  phone?: string;
  leg_status?: string;
  address?: string;
}

interface LegislatorProfileProps {
  legislator: Legislator;
  onClose: () => void;
}

interface SponsoredBill {
  bill_key: string;
  actual_bill_number: string;
  synopsis?: string;
  current_status?: string;
}

export default function LegislatorProfile({ legislator, onClose }: LegislatorProfileProps) {
  const [sponsoredBills, setSponsoredBills] = useState<SponsoredBill[]>([]);
  const [loadingSponsored, setLoadingSponsored] = useState(false);
  const [sponsoredError, setSponsoredError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [savedMessage, setSavedMessage] = useState<string | null>(null);

  const getFullName = () => {
    const parts = [legislator.first_name, legislator.mid_name, legislator.last_name, legislator.suffix].filter(Boolean);
    return parts.join(' ');
  };

  useEffect(() => {
    const fetchSponsoredBills = async () => {
      const sponsorName = [legislator.last_name, legislator.first_name].filter(Boolean).join(', ');
      if (!sponsorName) {
        setSponsoredBills([]);
        return;
      }

      if (!isSupabaseConfigured()) {
        setSponsoredError('Supabase is not configured. Set EXPO_PUBLIC_SUPABASE_URL and EXPO_PUBLIC_SUPABASE_ANON_KEY.');
        return;
      }

      setLoadingSponsored(true);
      setSponsoredError(null);

      const supabase = getSupabaseClient();
      if (!supabase) {
        setSponsoredError('Supabase is not configured. Set EXPO_PUBLIC_SUPABASE_URL and EXPO_PUBLIC_SUPABASE_ANON_KEY.');
        setLoadingSponsored(false);
        return;
      }

      const { data, error } = await supabase
        .from('bills')
        .select('bill_key, actual_bill_number, synopsis, current_status')
        .ilike('first_prime', `%${sponsorName}%`)
        .order('intro_date', { ascending: false })
        .limit(5);

      if (error) {
        console.error('Error loading sponsored bills:', error);
        setSponsoredError('Unable to load sponsored bills.');
      } else {
        setSponsoredBills(data || []);
      }

      setLoadingSponsored(false);
    };

    fetchSponsoredBills();
  }, [legislator]);

  const saveLegislator = async () => {
    if (!isSupabaseConfigured()) {
      setSavedMessage('Supabase is not configured. Configure it in Settings.');
      return;
    }
    const supabase = getSupabaseClient();
    if (!supabase) {
      setSavedMessage('Supabase is not configured. Configure it in Settings.');
      return;
    }

    setSaving(true);
    setSavedMessage(null);
    const { data: authData } = await supabase.auth.getUser();
    const user = authData.user;
    if (!user) {
      setSavedMessage('Sign in to save legislators.');
      setSaving(false);
      return;
    }

    const { error } = await supabase.from('user_saved_legislators').upsert({
      user_id: user.id,
      roster_key: legislator.roster_key,
    });
    if (error) {
      setSavedMessage('Unable to save legislator right now.');
    } else {
      setSavedMessage('Saved to your profile.');
    }
    setSaving(false);
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <View>
          <Text style={styles.name}>{getFullName()}</Text>
          <Text style={styles.details}>
            {legislator.party} • {legislator.house} • District {legislator.district}
          </Text>
          {legislator.leg_status && (
            <Text style={styles.statusText}>Status: {legislator.leg_status}</Text>
          )}
        </View>
        <TouchableOpacity style={styles.closeButton} onPress={onClose}>
          <Text style={styles.closeButtonText}>×</Text>
        </TouchableOpacity>
      </View>

      <ScrollView style={styles.content}>
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Contact Information</Text>
          <View style={styles.contactItem}>
            <Text style={styles.contactLabel}>Office Address:</Text>
            <Text style={styles.contactValue}>
              {legislator.address || 'Not available'}
            </Text>
          </View>
          <View style={styles.contactItem}>
            <Text style={styles.contactLabel}>Phone:</Text>
            <Text style={styles.contactValue}>
              {legislator.phone || 'Not available'}
            </Text>
          </View>
          <View style={styles.contactItem}>
            <Text style={styles.contactLabel}>Email:</Text>
            <Text style={styles.contactValue}>
              {legislator.email || 'Not available'}
            </Text>
          </View>
        </View>
        <TouchableOpacity style={styles.saveButton} onPress={saveLegislator} disabled={saving}>
          <Text style={styles.saveButtonText}>{saving ? 'Saving...' : 'Save Legislator'}</Text>
        </TouchableOpacity>
        {savedMessage && <Text style={styles.savedMessage}>{savedMessage}</Text>}

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Recent Voting Record</Text>
          <Text style={styles.emptyStateText}>
            Voting records are not yet connected. Provide a vote data source and we can surface recent roll-call votes here.
          </Text>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Sponsored Bills</Text>
          {loadingSponsored && (
            <Text style={styles.loadingText}>Loading sponsored bills...</Text>
          )}
          {sponsoredError && (
            <Text style={styles.errorText}>{sponsoredError}</Text>
          )}
          {!loadingSponsored && !sponsoredError && sponsoredBills.length === 0 && (
            <Text style={styles.emptyStateText}>
              No sponsored bills found yet.
            </Text>
          )}
          {!loadingSponsored && !sponsoredError && sponsoredBills.map((bill) => (
            <TouchableOpacity key={bill.bill_key} style={styles.billItem}>
              <Text style={styles.billId}>{bill.actual_bill_number || 'Unknown bill'}</Text>
              <Text style={styles.billTitle}>{bill.synopsis || 'No synopsis available'}</Text>
              <Text style={styles.billStatus}>Status: {bill.current_status || 'Unknown'}</Text>
            </TouchableOpacity>
          ))}
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#ffffff',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    padding: 20,
    backgroundColor: '#1e40af',
  },
  name: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#ffffff',
  },
  details: {
    fontSize: 16,
    color: '#bfdbfe',
    marginTop: 4,
  },
  statusText: {
    fontSize: 14,
    color: '#e2e8f0',
    marginTop: 4,
  },
  closeButton: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: 'rgba(255,255,255,0.2)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  closeButtonText: {
    color: '#ffffff',
    fontSize: 24,
    fontWeight: 'bold',
  },
  content: {
    flex: 1,
    padding: 16,
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1f2937',
    marginBottom: 12,
  },
  biographyText: {
    fontSize: 14,
    lineHeight: 20,
    color: '#374151',
  },
  saveButton: {
    backgroundColor: '#059669',
    borderRadius: 8,
    paddingVertical: 12,
    alignItems: 'center',
    marginBottom: 8,
  },
  saveButtonText: {
    color: '#ffffff',
    fontWeight: '600',
  },
  savedMessage: {
    color: '#059669',
    marginBottom: 12,
  },
  voteItem: {
    backgroundColor: '#f9fafb',
    padding: 12,
    borderRadius: 8,
    marginBottom: 8,
  },
  voteHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 4,
  },
  billTitle: {
    flex: 1,
    fontSize: 14,
    color: '#1f2937',
    marginRight: 8,
  },
  voteBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  voteText: {
    color: '#ffffff',
    fontSize: 12,
    fontWeight: '500',
  },
  voteDate: {
    fontSize: 12,
    color: '#6b7280',
  },
  billItem: {
    backgroundColor: '#f9fafb',
    padding: 12,
    borderRadius: 8,
    marginBottom: 8,
  },
  billId: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1e40af',
    marginBottom: 4,
  },
  billStatus: {
    fontSize: 12,
    color: '#6b7280',
    marginTop: 4,
  },
  loadingText: {
    fontSize: 14,
    color: '#6b7280',
  },
  errorText: {
    fontSize: 14,
    color: '#dc2626',
  },
  emptyStateText: {
    fontSize: 14,
    color: '#6b7280',
  },
  contactItem: {
    marginBottom: 8,
  },
  contactLabel: {
    fontSize: 14,
    fontWeight: '500',
    color: '#374151',
    marginBottom: 2,
  },
  contactValue: {
    fontSize: 14,
    color: '#6b7280',
  },
});
