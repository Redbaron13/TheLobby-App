import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity } from 'react-native';
import { supabase, isSupabaseConfigured } from '@/app/lib/supabase';

// Corrected interface to match the database table name 'legbio'
interface LegBio {
  Biography?: string;
  OfficeAddress?: string;
  OfficePhone?: string;
}

// Updated Legislator interface to use the correct property name
interface Legislator {
  RosterKey: number;
  Firstname: string;
  LastName: string;
  MidName?: string;
  Suffix?: string;
  Party: string;
  House: string;
  District: number;
  Title?: string;
  LegPos?: string;
  Email?: string;
  Phone?: string;
  legbio: LegBio | null; // Corrected from 'legisbio'
}

interface LegislatorProfileProps {
  legislator: Legislator;
  onClose: () => void;
}

interface SponsoredBill {
  billuuid: string;
  ActualBillNumber: string;
  Synopsis?: string;
  CurrentStatus?: string;
}

export default function LegislatorProfile({ legislator, onClose }: LegislatorProfileProps) {
  const [sponsoredBills, setSponsoredBills] = useState<SponsoredBill[]>([]);
  const [loadingSponsored, setLoadingSponsored] = useState(false);
  const [sponsoredError, setSponsoredError] = useState<string | null>(null);

  const getFullName = () => {
    const parts = [legislator.Firstname, legislator.MidName, legislator.LastName, legislator.Suffix].filter(Boolean);
    return parts.join(' ');
  };

  useEffect(() => {
    const fetchSponsoredBills = async () => {
      const sponsorName = [legislator.LastName, legislator.Firstname].filter(Boolean).join(', ');
      if (!sponsorName) {
        setSponsoredBills([]);
        return;
      }

      if (!isSupabaseConfigured || !supabase) {
        setSponsoredError('Supabase is not configured. Set EXPO_PUBLIC_SUPABASE_URL and EXPO_PUBLIC_SUPABASE_ANON_KEY.');
        return;
      }

      setLoadingSponsored(true);
      setSponsoredError(null);

      const { data, error } = await supabase
        .from('bills')
        .select('billuuid, "ActualBillNumber", "Synopsis", "CurrentStatus"')
        .ilike('FirstPrime', `%${sponsorName}%`)
        .order('IntroDate', { ascending: false })
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

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <View>
          <Text style={styles.name}>{getFullName()}</Text>
          <Text style={styles.details}>
            {legislator.Party} • {legislator.House} • District {legislator.District}
          </Text>
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
              {legislator.legbio?.OfficeAddress || 'Not available'}
            </Text>
          </View>
          <View style={styles.contactItem}>
            <Text style={styles.contactLabel}>Phone:</Text>
            <Text style={styles.contactValue}>
              {legislator.legbio?.OfficePhone || legislator.Phone || 'Not available'}
            </Text>
          </View>
          <View style={styles.contactItem}>
            <Text style={styles.contactLabel}>Email:</Text>
            <Text style={styles.contactValue}>
              {legislator.Email || 'Not available'}
            </Text>
          </View>
        </View>

        {legislator.legbio?.Biography && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Biography</Text>
            <Text style={styles.biographyText}>{legislator.legbio.Biography}</Text>
          </View>
        )}

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
            <TouchableOpacity key={bill.billuuid} style={styles.billItem}>
              <Text style={styles.billId}>{bill.ActualBillNumber || 'Unknown bill'}</Text>
              <Text style={styles.billTitle}>{bill.Synopsis || 'No synopsis available'}</Text>
              <Text style={styles.billStatus}>Status: {bill.CurrentStatus || 'Unknown'}</Text>
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
