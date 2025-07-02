import React, { useState, useEffect } from 'react';
import { View, Text, FlatList, TextInput, TouchableOpacity, Alert } from 'react-native';
import { supabase } from '@/app/lib/supabase';
import { styles as BillsScreenStyles } from './BillsScreenStyles'; // Corrected import

interface Bill {
  billuuid: string;
  BillType: string;
  BillNumber: number;
  ActualBillNumber: string;
  Synopsis: string;
  CurrentStatus: string;
  IntroDate: string;
  FirstPrime: string;
}

export function BillsScreen() {
  const [bills, setBills] = useState<Bill[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchBills();
  }, []);

  const fetchBills = async () => {
    try {
      setLoading(true);
      setError(null);

      console.log('Fetching bills from Supabase...');

      const { data, error } = await supabase
        .from('bills')
        .select(`
          billuuid,
          "BillType",
          "BillNumber",
          "ActualBillNumber",
          "Synopsis",
          "CurrentStatus",
          "IntroDate",
          "FirstPrime"
        `)
        .order('"BillNumber"', { ascending: false })
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
    bill.Synopsis?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    bill.ActualBillNumber?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    bill.FirstPrime?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const renderBill = ({ item }: { item: Bill }) => (
    <View style={BillsScreenStyles.billCard}>
      <Text style={BillsScreenStyles.billNumber}>
        {item.ActualBillNumber || `${item.BillType} ${item.BillNumber}`}
      </Text>
      <Text style={BillsScreenStyles.billSynopsis} numberOfLines={3}>
        {item.Synopsis || 'No synopsis available'}
      </Text>
      <Text style={BillsScreenStyles.billStatus}>
        Status: {item.CurrentStatus || 'Unknown'}
      </Text>
      {item.FirstPrime && (
        <Text style={BillsScreenStyles.billSponsor}>
          Primary Sponsor: {item.FirstPrime}
        </Text>
      )}
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
      />

      <Text style={BillsScreenStyles.resultCount}>
        Showing {filteredBills.length} of {bills.length} bills
      </Text>

      <FlatList
        data={filteredBills}
        renderItem={renderBill}
        keyExtractor={(item) => item.billuuid}
        style={BillsScreenStyles.billsList}
        showsVerticalScrollIndicator={false}
      />
    </View>
  );
}