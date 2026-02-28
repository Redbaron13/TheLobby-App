import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView, TouchableOpacity, TextInput, Alert, Modal, ActivityIndicator, StyleSheet } from 'react-native';
import { useSupabase } from '@/lib/supabase';
import LegislatorProfile from './LegislatorProfile';

// Corrected interface to match the database table name 'legbio'
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
}

export function LegislatorsScreen() {
  const { supabase, isConfigured } = useSupabase();
  const [searchTerm, setSearchTerm] = useState('');
  const [filterParty, setFilterParty] = useState('all');
  const [filterChamber, setFilterChamber] = useState('all');
  const [legislators, setLegislators] = useState<Legislator[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedLegislator, setSelectedLegislator] = useState<Legislator | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    loadLegislators();
  }, [supabase, isConfigured]);

  const loadLegislators = async () => {
    setLoading(true);
    try {
      if (!isConfigured || !supabase) {
        setErrorMessage('Supabase is not configured. Set EXPO_PUBLIC_SUPABASE_URL and EXPO_PUBLIC_SUPABASE_ANON_KEY.');
        return;
      }

      // Load bios when available, but do not exclude legislators without bios.
      const { data, error } = await supabase
        .from('legislators')
        .select('*, legbio(*)')
        .order('LastName');

      if (error) {
        console.error('Supabase error:', error);
        throw new Error(error.message);
      }

      setLegislators(data || []);
      setErrorMessage(null);

    } catch (error) {
      console.error('Error loading legislators:', error);
      Alert.alert('Error', 'Failed to load legislators. Please check your network connection and Supabase RLS policies.');
      setErrorMessage('Failed to load legislators. Please check your network connection and Supabase policies.');
    } finally {
      setLoading(false);
    }
  };

  const getFullName = (legislator: Legislator) => {
    const parts = [legislator.first_name, legislator.mid_name, legislator.last_name, legislator.suffix].filter(Boolean);
    return parts.join(' ');
  };

  const getPartyColor = (party: string) => {
    if (party?.toLowerCase().includes('democrat')) return '#059669';
    if (party?.toLowerCase().includes('republican')) return '#7c3aed';
    return '#64748b';
  };

  const filteredLegislators = legislators.filter(legislator => {
    const fullName = getFullName(legislator);
    const matchesSearch = fullName.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesParty = filterParty === 'all' || (legislator.party && legislator.party.toLowerCase().includes(filterParty.toLowerCase()));
    const matchesChamber = filterChamber === 'all' || (legislator.house && legislator.house.toLowerCase() === filterChamber.toLowerCase());
    return matchesSearch && matchesParty && matchesChamber;
  });

  // Corrected renderContent function
  const renderContent = () => {
    if (loading) {
      return <ActivityIndicator size="large" color="#0f172a" style={{ marginTop: 20 }} />;
    }

    if (errorMessage) {
      return (
        <Text style={styles.infoText}>
          {errorMessage}
        </Text>
      );
    }

    if (legislators.length === 0) {
      return (
        <Text style={styles.infoText}>
          No legislators found. There might be an issue with the data source or RLS policies.
        </Text>
      );
    }

    if (filteredLegislators.length === 0) {
      return (
        <Text style={styles.infoText}>
          No legislators match your search criteria.
        </Text>
      );
    }

    return filteredLegislators.map(legislator => (
      <TouchableOpacity
        key={legislator.roster_key}
        onPress={() => setSelectedLegislator(legislator)}
        style={styles.legislatorCard}
      >
        <View style={styles.legislatorHeader}>
          <Text style={styles.legislatorName}>
            {getFullName(legislator)}
          </Text>
          <View style={[styles.partyBadge, { backgroundColor: getPartyColor(legislator.party) }]}>
            <Text style={styles.partyText}>
              {legislator.party?.charAt(0) || 'I'}
            </Text>
          </View>
        </View>
        <Text style={styles.legislatorInfo}>
          {legislator.house} - District {legislator.district}
        </Text>
        {legislator.leg_pos && (
          <Text style={styles.leadershipPosition}>
            {legislator.leg_pos}
          </Text>
        )}
        {legislator.leg_status && (
          <Text style={styles.statusText}>
            Status: {legislator.leg_status}
          </Text>
        )}
      </TouchableOpacity>
    ));
  };


  return (
    <View style={styles.container}>
      <ScrollView style={styles.scrollView}>
        <View style={styles.header}>
          <Text style={styles.title}>
            All Legislators
          </Text>

          <TextInput
            style={styles.searchInput}
            placeholder="Search legislators..."
            value={searchTerm}
            onChangeText={setSearchTerm}
            placeholderTextColor="#94a3b8"
          />

          <View style={{ marginBottom: 8 }}>
            <View style={{ flexDirection: 'row', gap: 8, marginBottom: 8 }}>
              {['all', 'senate', 'assembly'].map(chamber => (
                <TouchableOpacity
                  key={chamber}
                  style={[styles.filterButton, filterChamber === chamber && styles.activeFilter]}
                  onPress={() => setFilterChamber(chamber)}
                >
                  <Text style={[styles.filterText, filterChamber === chamber && styles.activeFilterText]}>
                    {chamber.charAt(0).toUpperCase() + chamber.slice(1)}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
            <View style={{ flexDirection: 'row', gap: 8 }}>
              {['all', 'democrat', 'republican'].map(party => (
                <TouchableOpacity
                  key={party}
                  style={[styles.filterButton, filterParty === party && styles.activeFilter]}
                  onPress={() => setFilterParty(party)}
                >
                  <Text style={[styles.filterText, filterParty === party && styles.activeFilterText]}>
                    {party.charAt(0).toUpperCase() + party.slice(1)}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>
        </View>

        <View style={styles.content}>{renderContent()}</View>

      </ScrollView>

      <Modal
        animationType="slide"
        transparent={false}
        visible={selectedLegislator !== null}
        onRequestClose={() => {
          setSelectedLegislator(null);
        }}
      >
        {selectedLegislator && (
          <LegislatorProfile
            legislator={selectedLegislator}
            onClose={() => setSelectedLegislator(null)}
          />
        )}
      </Modal>
    </View>
  );
}

// Added StyleSheet for better organization
const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  scrollView: {
    flex: 1,
    backgroundColor: '#f1f5f9'
  },
  header: {
    padding: 16,
    backgroundColor: '#ffffff',
    borderBottomWidth: 1,
    borderBottomColor: '#e2e8f0'
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1e293b',
    marginBottom: 16
  },
  searchInput: {
    backgroundColor: '#f8fafc',
    borderWidth: 1,
    borderColor: '#e2e8f0',
    borderRadius: 8,
    padding: 12,
    marginBottom: 16,
    fontSize: 16,
  },
  filterButton: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    backgroundColor: '#e2e8f0',
  },
  activeFilter: {
    backgroundColor: '#0f172a',
  },
  filterText: {
    color: '#64748b',
    fontWeight: '600',
    fontSize: 14,
  },
  activeFilterText: {
    color: '#ffffff',
  },
  content: {
    padding: 16,
  },
  infoText: {
    textAlign: 'center',
    color: '#64748b',
    fontSize: 16,
    marginTop: 20
  },
  legislatorCard: {
    backgroundColor: '#ffffff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    boxShadow: '0px 2px 4px rgba(0, 0, 0, 0.1)',
    elevation: 3,
  },
  legislatorHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8
  },
  legislatorName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1e293b',
    flex: 1
  },
  partyBadge: {
    width: 32,
    height: 32,
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
  },
  partyText: {
    color: '#ffffff',
    fontWeight: 'bold',
    fontSize: 16
  },
  legislatorInfo: {
    color: '#64748b',
    fontSize: 16,
    marginBottom: 4
  },
  leadershipPosition: {
    color: '#059669',
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 4
  },
  statusText: {
    color: '#94a3b8',
    fontSize: 13,
  },
});

export default LegislatorsScreen;
