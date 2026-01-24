import React, { useState } from 'react';
import { View, Text, ScrollView, TouchableOpacity, Alert, TextInput, ActivityIndicator } from 'react-native';
import * as Location from 'expo-location';
import { getSupabaseClient, isSupabaseConfigured } from '@/app/lib/supabase';

interface Legislator {
  roster_key: number;
  first_name: string;
  last_name: string;
  party: string;
  house: string;
  district: number;
  leg_pos?: string;
  leg_status?: string;
}

export function FindLegislatorScreen() {
  const [location, setLocation] = useState<Location.LocationObject | null>(null);
  const [address, setAddress] = useState<Location.LocationGeocodedAddress | null>(null);
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [districtInput, setDistrictInput] = useState('');
  const [districtReps, setDistrictReps] = useState<Legislator[]>([]);
  const [districtLoading, setDistrictLoading] = useState(false);

  const findMyLocation = async () => {
    setLoading(true);
    setErrorMessage(null);
    try {
      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== 'granted') {
        setErrorMessage('Location permission was denied. Please enable it to use automatic lookup.');
        return;
      }

      const currentLocation = await Location.getCurrentPositionAsync({
        accuracy: Location.Accuracy.Balanced
      });
      setLocation(currentLocation);

      const [reverseGeocode] = await Location.reverseGeocodeAsync(currentLocation.coords);
      setAddress(reverseGeocode ?? null);
    } catch (error) {
      console.error('Location error:', error);
      Alert.alert('Error', 'Could not get location');
    } finally {
      setLoading(false);
    }
  };

  const lookupDistrict = async () => {
    const districtNumber = Number(districtInput);
    if (!districtInput || Number.isNaN(districtNumber)) {
      setErrorMessage('Enter a valid legislative district number.');
      return;
    }

    if (!isSupabaseConfigured()) {
      setErrorMessage('Supabase is not configured. Set EXPO_PUBLIC_SUPABASE_URL and EXPO_PUBLIC_SUPABASE_ANON_KEY.');
      return;
    }

    setDistrictLoading(true);
    setErrorMessage(null);
    setDistrictReps([]);

    const supabase = getSupabaseClient();
    if (!supabase) {
      setErrorMessage('Supabase is not configured. Set EXPO_PUBLIC_SUPABASE_URL and EXPO_PUBLIC_SUPABASE_ANON_KEY.');
      setDistrictLoading(false);
      return;
    }

    const { data, error } = await supabase
      .from('legislators')
      .select('roster_key, first_name, last_name, party, house, district, leg_pos, leg_status')
      .eq('district', districtNumber)
      .order('house');

    if (error) {
      console.error('District lookup error:', error);
      setErrorMessage('Unable to load legislators for that district.');
    } else {
      setDistrictReps(data || []);
    }

    setDistrictLoading(false);
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

        {errorMessage && (
          <Text style={{ color: '#dc2626', marginBottom: 16 }}>
            {errorMessage}
          </Text>
        )}
        
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
              Latitude: {location.coords.latitude.toFixed(4)}
            </Text>
            <Text style={{ color: '#64748b' }}>
              Longitude: {location.coords.longitude.toFixed(4)}
            </Text>
            {address && (
              <Text style={{ color: '#64748b', marginTop: 8 }}>
                {address.city || address.subregion || ''}{address.postalCode ? ` • ${address.postalCode}` : ''}
              </Text>
            )}
            <Text style={{ color: '#059669', marginTop: 8 }}>
              Automatic district matching uses NJ GIS boundaries in the backend.
            </Text>
          </View>
        )}

        <View style={{ marginTop: 24 }}>
          <Text style={{ fontSize: 18, fontWeight: 'bold', color: '#1e293b', marginBottom: 8 }}>
            Look up by district
          </Text>
          <TextInput
            style={{
              backgroundColor: '#ffffff',
              borderRadius: 10,
              padding: 12,
              borderWidth: 1,
              borderColor: '#e2e8f0',
              marginBottom: 12,
            }}
            placeholder="Enter district number (1-40)"
            keyboardType="numeric"
            value={districtInput}
            onChangeText={setDistrictInput}
          />
          <TouchableOpacity
            style={{
              backgroundColor: '#059669',
              padding: 14,
              borderRadius: 10,
              alignItems: 'center',
              marginBottom: 16,
            }}
            onPress={lookupDistrict}
            disabled={districtLoading}
          >
            <Text style={{ color: '#ffffff', fontWeight: '600' }}>
              {districtLoading ? 'Searching...' : 'Search District'}
            </Text>
          </TouchableOpacity>
          {districtLoading && <ActivityIndicator size="small" color="#0f172a" />}
          {!districtLoading && districtReps.length > 0 && (
            <View>
              {districtReps.map(rep => (
                <View key={rep.roster_key} style={{
                  backgroundColor: '#ffffff',
                  borderRadius: 12,
                  padding: 12,
                  marginBottom: 10,
                  shadowColor: '#000',
                  shadowOffset: { width: 0, height: 2 },
                  shadowOpacity: 0.1,
                  shadowRadius: 4,
                  elevation: 2,
                }}>
                  <Text style={{ fontSize: 16, fontWeight: '600', color: '#1e293b' }}>
                    {rep.first_name} {rep.last_name}
                  </Text>
                  <Text style={{ color: '#64748b' }}>
                    {rep.house} • District {rep.district} • {rep.party}
                  </Text>
                  {rep.leg_pos && (
                    <Text style={{ color: '#059669', marginTop: 4 }}>
                      {rep.leg_pos}
                    </Text>
                  )}
                  {rep.leg_status && (
                    <Text style={{ color: '#94a3b8', marginTop: 4 }}>
                      Status: {rep.leg_status}
                    </Text>
                  )}
                </View>
              ))}
            </View>
          )}
          {!districtLoading && districtInput && districtReps.length === 0 && !errorMessage && (
            <Text style={{ color: '#64748b' }}>
              No legislators found for that district.
            </Text>
          )}
        </View>
      </View>
    </ScrollView>
  );
}

export default FindLegislatorScreen;
