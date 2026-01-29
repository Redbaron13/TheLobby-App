import React, { useState, useEffect } from 'react';
import { View, Text, FlatList, TouchableOpacity, Alert, ActivityIndicator } from 'react-native';
import { supabase, isSupabaseConfigured } from '@/app/lib/supabase';
import { styles } from './AdminScreenStyles';

interface ValidationIssue {
  issue_id: string;
  table_name: string;
  record_key: string | null;
  issue: string;
  details: string | null;
  raw_data: string | null;
  run_date: string | null;
  created_at: string;
}

export function AdminScreen() {
  const [issues, setIssues] = useState<ValidationIssue[]>([]);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [selectedTable, setSelectedTable] = useState<string | null>(null);
  const [expandedIssues, setExpandedIssues] = useState<Set<string>>(new Set());

  useEffect(() => {
    fetchIssues();
  }, []);

  const fetchIssues = async () => {
    setLoading(true);
    if (!isSupabaseConfigured || !supabase) {
      setLoading(false);
      return;
    }

    try {
      const { data, error } = await supabase
        .from('data_validation_issues')
        .select('*')
        .order('created_at', { ascending: false })
        .limit(100);

      if (error) throw error;
      setIssues(data || []);
    } catch (err) {
      console.error('Error fetching issues:', err);
      Alert.alert('Error', 'Failed to load validation issues.');
    } finally {
      setLoading(false);
    }
  };

  const triggerPipeline = async () => {
    setSyncing(true);
    // Mock pipeline trigger
    // In a real scenario, this would call an Edge Function or API endpoint
    // that invokes the Python pipeline.
    setTimeout(() => {
      setSyncing(false);
      Alert.alert('Pipeline Triggered', 'The data synchronization pipeline has been initiated. Check back later for results.');
      fetchIssues(); // Reload issues after trigger (assuming quick run for mock)
    }, 2000);
  };

  const toggleExpand = (id: string) => {
    const newExpanded = new Set(expandedIssues);
    if (newExpanded.has(id)) {
      newExpanded.delete(id);
    } else {
      newExpanded.add(id);
    }
    setExpandedIssues(newExpanded);
  };

  const tables = Array.from(new Set(issues.map(i => i.table_name))).sort();

  const filteredIssues = selectedTable
    ? issues.filter(i => i.table_name === selectedTable)
    : issues;

  const renderItem = ({ item }: { item: ValidationIssue }) => (
    <View style={styles.issueCard}>
      <View style={styles.issueHeader}>
        <Text style={styles.issueTable}>{item.table_name}</Text>
        <Text style={styles.issueDate}>{item.run_date}</Text>
      </View>
      <Text style={styles.issueType}>{item.issue}</Text>
      <Text style={styles.issueDetails}>{item.details || 'No details'}</Text>

      {item.raw_data && (
        <View>
          <TouchableOpacity
            style={styles.expandButton}
            onPress={() => toggleExpand(item.issue_id)}
          >
            <Text style={styles.expandText}>
              {expandedIssues.has(item.issue_id) ? 'Hide Raw Data' : 'Show Raw Data'}
            </Text>
          </TouchableOpacity>

          {expandedIssues.has(item.issue_id) && (
            <View style={styles.rawContainer}>
              <Text style={styles.rawText}>{item.raw_data}</Text>
            </View>
          )}
        </View>
      )}
    </View>
  );

  if (!isSupabaseConfigured) {
    return (
      <View style={styles.container}>
        <Text style={styles.emptyText}>Supabase is not configured.</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Admin Dashboard</Text>
      </View>

      <View style={styles.controlPanel}>
        <Text style={styles.controlTitle}>Pipeline Control</Text>
        <TouchableOpacity
          style={[styles.syncButton, syncing && { opacity: 0.7 }]}
          onPress={triggerPipeline}
          disabled={syncing}
        >
          {syncing ? (
             <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.syncButtonText}>Force Data Sync (Manual)</Text>
          )}
        </TouchableOpacity>
      </View>

      <View style={styles.header}>
        <Text style={styles.title}>Validation Issues</Text>
        <TouchableOpacity onPress={fetchIssues}>
           <Text style={styles.expandText}>Refresh</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.filterContainer}>
        <TouchableOpacity
          style={[styles.filterButton, !selectedTable && styles.filterButtonActive]}
          onPress={() => setSelectedTable(null)}
        >
          <Text style={[styles.filterText, !selectedTable && styles.filterTextActive]}>All</Text>
        </TouchableOpacity>
        {tables.map(table => (
          <TouchableOpacity
            key={table}
            style={[styles.filterButton, selectedTable === table && styles.filterButtonActive]}
            onPress={() => setSelectedTable(table)}
          >
            <Text style={[styles.filterText, selectedTable === table && styles.filterTextActive]}>
              {table}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {loading ? (
        <ActivityIndicator size="large" color="#38bdf8" style={{ marginTop: 20 }} />
      ) : (
        <FlatList
          data={filteredIssues}
          renderItem={renderItem}
          keyExtractor={item => item.issue_id}
          style={styles.list}
          ListEmptyComponent={
            <Text style={styles.emptyText}>No validation issues found.</Text>
          }
        />
      )}
    </View>
  );
}
