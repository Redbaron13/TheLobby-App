import React, { useState } from 'react';
import { View, Text, ScrollView, TouchableOpacity, Alert } from 'react-native';

export function FindLegislatorScreen() {
  const [location, setLocation] = useState<{latitude: number, longitude: number} | null>(null);
  const [loading, setLoading] = useState(false);

  const findMyLocation = async () => {
    setLoading(true);
    try {
      // Simple mock location for NJ
      const mockLocation = {
        latitude: 40.0583,
        longitude: -74.4057
      };
      setLocation(mockLocation);
      Alert.alert('Location Found', 'Using sample NJ location. In production, this would use GPS.');
    } catch (error) {
      Alert.alert('Error', 'Could not get location');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView style={{ flex: 1, backgroundColor: '#f1f5f9' }}>
      <View style={{ padding: 16 }}>
        <Text style={{ fontSize: 24, fontWeight: 'bold', color: '#1e293b', marginBottom: 16 }}>
          Find Your Legislator
        </Text>
        
        <Text style={{ fontSize: 16, color: '#64748b', marginBottom: 20 }}>
          Use your location to find your representatives in the NJ Legislature.
        </Text>
        
        <TouchableOpacity
          style={{
            backgroundColor: '#0f172a',
            padding: 16,
            borderRadius: 12,
            alignItems: 'center',
            marginBottom: 20,
          }}
          onPress={findMyLocation}
          disabled={loading}
        >
          <Text style={{ color: '#ffffff', fontSize: 16, fontWeight: '600' }}>
            {loading ? 'Finding Location...' : 'Find My Location'}
          </Text>
        </TouchableOpacity>
        
        {location && (
          <View style={{
            backgroundColor: '#ffffff',
            borderRadius: 12,
            padding: 16,
            shadowColor: '#000',
            shadowOffset: { width: 0, height: 2 },
            shadowOpacity: 0.1,
            shadowRadius: 4,
            elevation: 3,
          }}>
            <Text style={{ fontSize: 18, fontWeight: 'bold', color: '#1e293b', marginBottom: 8 }}>
              Your Location
            </Text>
            <Text style={{ color: '#64748b' }}>
              Latitude: {location.latitude.toFixed(4)}
            </Text>
            <Text style={{ color: '#64748b' }}>
              Longitude: {location.longitude.toFixed(4)}
            </Text>
            <Text style={{ color: '#059669', marginTop: 8 }}>
              Feature coming soon: District lookup based on coordinates
            </Text>
          </View>
        )}
      </View>
    </ScrollView>
  );
}

export default FindLegislatorScreen;