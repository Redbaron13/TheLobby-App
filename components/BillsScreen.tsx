import React, { useState, useEffect } from 'react';
import { View, Text, FlatList, TextInput, TouchableOpacity } from 'react-native';
import { useSupabase } from '@/app/lib/supabase.tsx';
import { styles as BillsScreenStyles } from './BillsScreenStyles'; // Corrected import

interface Bill {
  bill_key: string;
  bill_type: string;
  bill_number: number;
  actual_bill_number: string;
  synopsis: string;
  current_status: string;
  intro_date: string;
  first_prime: string;
}

export function BillsScreen() {
  const { supabase, isConfigured } = useSupabase();
  const [bills, setBills] = useState<Bill[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchBills();
  }, [supabase, isConfigured]);

  const fetchBills = async () => {
    try {
      setLoading(true);
      setError(null);

      console.log('Fetching bills from Supabase...');

      if (!isConfigured || !supabase) {
        setError('Supabase is not configured. Set EXPO_PUBLIC_SUPABASE_URL and EXPO_PUBLIC_SUPABASE_ANON_KEY.');
        return;
      }

      const { data, error } = await supabase
        .from('bills')
        .select(`
          bill_key,
          bill_type,
          bill_number,
          actual_bill_number,
          synopsis,
          current_status,
          intro_date,
          first_prime
        `)
        .order('BillNumber', { ascending: false })
        .limit(50);

      if (error) {
        console.error('Supabase error:', error);
        setError(`Database error: ${error.message}`);
        return;
      }

      console.log('Bills fetched successfully:', data?.length || 0);
      setBills(data || []);

    } catch (err) {
      console.error('Fetch error:', err);
      setError(`Fetch error: ${err}`);
    } finally {
      setLoading(false);
    }
  };

  const filteredBills = bills.filter(bill =>
    bill.synopsis?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    bill.actual_bill_number?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    bill.first_prime?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const [actionMessage, setActionMessage] = useState<string | null>(null);

  const saveBill = async (bill: Bill) => {
    if (!isConfigured || !supabase) {
      setActionMessage('Supabase is not configured. Configure it in Settings.');
      return;
    }

    const { data: authData } = await supabase.auth.getUser();
    const user = authData.user;
    if (!user) {
      setActionMessage('Sign in to save bills.');
      return;
    }
    const { error } = await supabase.from('user_saved_bills').upsert({
      user_id: user.id,
      bill_key: bill.bill_key,
    });
    if (error) {
      setActionMessage('Unable to save bill right now.');
    } else {
      setActionMessage('Saved to your profile.');
    }
  };

  const renderBill = ({ item }: { item: Bill }) => (
    <View style={BillsScreenStyles.billCard}>
      <Text style={BillsScreenStyles.billNumber}>
        {item.actual_bill_number || `${item.bill_type} ${item.bill_number}`}
      </Text>
      <Text style={BillsScreenStyles.billSynopsis} numberOfLines={3}>
        {item.synopsis || 'No synopsis available'}
      </Text>
      <Text style={BillsScreenStyles.billStatus}>
        Status: {item.current_status || 'Unknown'}
      </Text>
      {item.first_prime && (
        <Text style={BillsScreenStyles.billSponsor}>
          Primary Sponsor: {item.first_prime}
        </Text>
      )}
      <TouchableOpacity style={BillsScreenStyles.saveButton} onPress={() => saveBill(item)}>
        <Text style={BillsScreenStyles.saveButtonText}>Save Bill</Text>
      </TouchableOpacity>
    </View>
  );

  if (loading) {
    return (
      <View style={BillsScreenStyles.container}>
        <Text style={BillsScreenStyles.loadingText}>Loading bills...</Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={BillsScreenStyles.container}>
        <Text style={BillsScreenStyles.errorText}>{error}</Text>
        <TouchableOpacity
          style={BillsScreenStyles.retryButton}
          onPress={fetchBills}
        >
          <Text style={BillsScreenStyles.retryButtonText}>Retry</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <View style={BillsScreenStyles.container}>
      <Text style={BillsScreenStyles.title}>New Jersey Bills</Text>

      <TextInput
        style={BillsScreenStyles.searchInput}
        placeholder="Search bills..."
        value={searchTerm}
        onChangeText={setSearchTerm}
        placeholderTextColor="#e2e8f0"
      />

      <Text style={BillsScreenStyles.resultCount}>
        Showing {filteredBills.length} of {bills.length} bills
      </Text>
      {actionMessage && (
        <Text style={BillsScreenStyles.actionMessage}>{actionMessage}</Text>
      )}

      <FlatList
        data={filteredBills}
        renderItem={renderBill}
        keyExtractor={(item) => item.bill_key}
        style={BillsScreenStyles.billsList}
        showsVerticalScrollIndicator={false}
        ListEmptyComponent={
          <Text style={BillsScreenStyles.emptyStateText}>
            No bills match your search right now.
          </Text>
        }
      />
    </View>
  );
}
