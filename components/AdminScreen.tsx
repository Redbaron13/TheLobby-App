import React, { useState, useEffect } from 'react';
import { View, Text, FlatList, TouchableOpacity, Alert, ActivityIndicator, Modal, ScrollView } from 'react-native';
import { useSupabase } from '@/app/lib/supabase';
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
  const { supabase, isConfigured } = useSupabase();
  const [issues, setIssues] = useState<ValidationIssue[]>([]);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [backendStatus, setBackendStatus] = useState<any>(null);
  const [selectedTable, setSelectedTable] = useState<string | null>(null);
  const [expandedIssues, setExpandedIssues] = useState<Set<string>>(new Set());

  const [isInitModalVisible, setIsInitModalVisible] = useState(false);
  const [initLogs, setInitLogs] = useState<string[]>([]);
  const [initializing, setInitializing] = useState(false);


  const backendUrl = process.env.EXPO_PUBLIC_BACKEND_API_URL || 'http://localhost:8000';

  useEffect(() => {
    fetchIssues();
    fetchBackendStatus();
    const interval = setInterval(fetchBackendStatus, 5000);
    return () => clearInterval(interval);
  }, [supabase, isConfigured]);

  const fetchBackendStatus = async () => {
    try {
      const response = await fetch(`${backendUrl}/status`);
      const data = await response.json();
      setBackendStatus(data);
      if (data.status === 'running') {
        setSyncing(true);
      } else {
        setSyncing(false);
      }
    } catch (err) {
      console.error('Error fetching backend status:', err);
    }
  };

  const fetchIssues = async () => {
    setLoading(true);
    if (!isConfigured || !supabase) {
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
    try {
      const response = await fetch(`${backendUrl}/sync`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({}),
      });

      if (response.status === 409) {
        Alert.alert('Pipeline Running', 'A data synchronization is already in progress.');
        return;
      }

      if (!response.ok) throw new Error('Failed to trigger pipeline');
      Alert.alert('Pipeline Triggered', 'The data synchronization pipeline has been initiated.');
    } catch (err) {
      console.error('Error triggering pipeline:', err);
      Alert.alert('Error', 'Failed to trigger the pipeline.');
      setSyncing(false);
    }
  };


  const addInitLog = (msg: string) => {
    setInitLogs(prev => [...prev, `${new Date().toLocaleTimeString()}: ${msg}`]);
  };

  const startInit = async () => {
    setInitializing(true);
    setInitLogs([]);
    addInitLog('Starting database initialization...');
    try {
      addInitLog(`Calling backend init endpoint at ${backendUrl}/init...`);
      const response = await fetch(`${backendUrl}/init`, { method: 'POST' });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to initialize database');
      }

      addInitLog('Database schema initialized successfully.');
      Alert.alert('Success', 'Database initialized successfully.');

    } catch (err: any) {
      console.error('Error initializing database:', err);
      if (err.message === 'Failed to fetch' || err.message.includes('Network Error')) {
        const errorMsg = `Network Error: Could not reach backend at ${backendUrl}. Ensure the Python backend is running (e.g., uvicorn backend.api:app --reload) and EXPO_PUBLIC_BACKEND_API_URL is set correctly (use your local IP instead of localhost on physical devices).`;
        addInitLog(errorMsg);
        Alert.alert('Backend Unreachable', errorMsg);
      } else {
        addInitLog(`Error: ${err.message || 'Failed to initialize database.'}`);
        Alert.alert('Error', 'Failed to initialize database. Check logs.');
      }
    } finally {

      setInitializing(false);
    }
  };

  const triggerInit = () => {
    setIsInitModalVisible(true);
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

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Admin Dashboard</Text>
      </View>

      <View style={styles.controlPanel}>
        <Text style={styles.controlTitle}>Pipeline Control</Text>
        {backendStatus && (
          <View style={{ marginBottom: 10 }}>
            <Text style={{ color: '#fff' }}>Status: {backendStatus.status}</Text>
            {backendStatus.last_run && (
              <Text style={{ color: '#94a3b8', fontSize: 12 }}>Last run: {new Date(backendStatus.last_run).toLocaleString()}</Text>
            )}
          </View>
        )}
        <View style={{ flexDirection: 'row', gap: 10 }}>
          <TouchableOpacity
            style={[styles.syncButton, { flex: 1 }, syncing && { opacity: 0.7 }]}
            onPress={triggerPipeline}
            disabled={syncing}
          >
            {syncing ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={styles.syncButtonText}>Run Data Sync</Text>
            )}
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.syncButton, { flex: 1, backgroundColor: '#475569' }]}
            onPress={triggerInit}
          >
            <Text style={styles.syncButtonText}>Init Database</Text>
          </TouchableOpacity>
        </View>
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

      {!isConfigured && (
        <Text style={[styles.emptyText, { marginBottom: 20 }]}>
          Note: Supabase is not configured in the frontend. Issue tracking may be unavailable.
        </Text>
      )}

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
