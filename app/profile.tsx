import React from 'react';
import { View, Text, ScrollView } from 'react-native';

export default function Profile() {
  return (
    <ScrollView style={{ flex: 1, backgroundColor: '#f1f5f9' }}>
      <View style={{ backgroundColor: '#0f172a', padding: 20 }}>
        <Text style={{ fontSize: 28, fontWeight: 'bold', color: '#ffffff' }}>Profile</Text>
      </View>
      <View style={{ padding: 16 }}>
        <Text style={{ fontSize: 16, color: '#64748b' }}>User profile coming soon...</Text>
      </View>
    </ScrollView>
  );
}