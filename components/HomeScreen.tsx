import React from 'react';
import { View, Text, ScrollView, TouchableOpacity } from 'react-native';
import { useRouter } from 'expo-router';

export function HomeScreen() {
  const router = useRouter();

  return (
    <ScrollView style={{ flex: 1, backgroundColor: '#f1f5f9' }}>
      <View style={{ backgroundColor: '#0f172a', padding: 24, alignItems: 'center' }}>
        <Text style={{ fontSize: 36, fontWeight: 'bold', color: '#ffffff', letterSpacing: 1 }}>
          The Lobby
        </Text>
        <Text style={{ fontSize: 18, color: '#94a3b8', marginTop: 6 }}>
          NJ Legislative Tracker
        </Text>
      </View>
      
      <View style={{ padding: 20 }}>
        <Text style={{ fontSize: 24, fontWeight: '700', color: '#1e293b', marginBottom: 16 }}>
          Legislative Chambers
        </Text>
        
        <TouchableOpacity 
          style={{
            backgroundColor: '#ffffff',
            borderRadius: 16,
            padding: 20,
            marginBottom: 20,
            shadowColor: '#000',
            shadowOffset: { width: 0, height: 4 },
            shadowOpacity: 0.15,
            shadowRadius: 8,
            elevation: 5,
          }}
          onPress={() => router.push('/senate')}
        >
          <Text style={{ fontSize: 28, fontWeight: '700', color: '#1e293b', marginBottom: 8, textAlign: 'center' }}>
            State Senate
          </Text>
          <Text style={{ fontSize: 16, color: '#64748b', textAlign: 'center' }}>
            40 Members
          </Text>
        </TouchableOpacity>
        
        <TouchableOpacity 
          style={{
            backgroundColor: '#ffffff',
            borderRadius: 16,
            padding: 20,
            marginBottom: 20,
            shadowColor: '#000',
            shadowOffset: { width: 0, height: 4 },
            shadowOpacity: 0.15,
            shadowRadius: 8,
            elevation: 5,
          }}
          onPress={() => router.push('/assembly')}
        >
          <Text style={{ fontSize: 28, fontWeight: '700', color: '#1e293b', marginBottom: 8, textAlign: 'center' }}>
            General Assembly
          </Text>
          <Text style={{ fontSize: 16, color: '#64748b', textAlign: 'center' }}>
            80 Members
          </Text>
        </TouchableOpacity>
        
        <View style={{ marginTop: 24 }}>
          <Text style={{ fontSize: 24, fontWeight: '700', color: '#1e293b', marginBottom: 16 }}>
            Quick Actions
          </Text>
          <TouchableOpacity 
            style={{
              backgroundColor: '#ffffff',
              padding: 18,
              borderRadius: 12,
              marginBottom: 12,
              shadowColor: '#000',
              shadowOffset: { width: 0, height: 2 },
              shadowOpacity: 0.1,
              shadowRadius: 4,
              elevation: 3,
            }}
            onPress={() => router.push('/find-legislator')}
          >
            <Text style={{ fontSize: 16, color: '#0f172a', fontWeight: '600', textAlign: 'center' }}>
              Find My Representatives
            </Text>
          </TouchableOpacity>
          <TouchableOpacity 
            style={{
              backgroundColor: '#ffffff',
              padding: 18,
              borderRadius: 12,
              marginBottom: 12,
              shadowColor: '#000',
              shadowOffset: { width: 0, height: 2 },
              shadowOpacity: 0.1,
              shadowRadius: 4,
              elevation: 3,
            }}
            onPress={() => router.push('/legislators')}
          >
            <Text style={{ fontSize: 16, color: '#0f172a', fontWeight: '600', textAlign: 'center' }}>
              All Legislators
            </Text>
          </TouchableOpacity>
          <TouchableOpacity 
            style={{
              backgroundColor: '#ffffff',
              padding: 18,
              borderRadius: 12,
              marginBottom: 12,
              shadowColor: '#000',
              shadowOffset: { width: 0, height: 2 },
              shadowOpacity: 0.1,
              shadowRadius: 4,
              elevation: 3,
            }}
            onPress={() => router.push('/bills')}
          >
            <Text style={{ fontSize: 16, color: '#0f172a', fontWeight: '600', textAlign: 'center' }}>
              Search Bills
            </Text>
          </TouchableOpacity>
        </View>
      </View>
    </ScrollView>
  );
}

export default HomeScreen;