import React from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity } from 'react-native';

interface Seat {
  id: number;
  legislator?: string;
  party?: 'Democrat' | 'Republican';
  district?: string;
  vacant?: boolean;
}

interface ChamberViewProps {
  chamber: 'Assembly' | 'Senate';
  onSeatPress: (seat: Seat) => void;
}

export default function ChamberView({ chamber, onSeatPress }: ChamberViewProps) {
  // Mock data for demonstration
  const assemblySeats: Seat[] = Array.from({ length: 80 }, (_, i) => ({
    id: i + 1,
    legislator: i < 52 ? `Legislator ${i + 1}` : i < 80 ? `Legislator ${i + 1}` : undefined,
    party: i < 52 ? 'Democrat' : i < 80 ? 'Republican' : undefined,
    district: `${i + 1}`,
    vacant: i >= 80
  }));

  const senateSeats: Seat[] = Array.from({ length: 40 }, (_, i) => ({
    id: i + 1,
    legislator: i < 25 ? `Senator ${i + 1}` : i < 40 ? `Senator ${i + 1}` : undefined,
    party: i < 25 ? 'Democrat' : i < 40 ? 'Republican' : undefined,
    district: `${i + 1}`,
    vacant: i >= 40
  }));

  const seats = chamber === 'Assembly' ? assemblySeats : senateSeats;
  const seatsPerRow = chamber === 'Assembly' ? 10 : 8;

  const getSeatColor = (seat: Seat) => {
    if (seat.vacant) return '#9ca3af';
    if (seat.party === 'Democrat') return '#2563eb';
    if (seat.party === 'Republican') return '#dc2626';
    return '#6b7280';
  };

  const renderSeatGrid = () => {
    const rows = [];
    for (let i = 0; i < seats.length; i += seatsPerRow) {
      const rowSeats = seats.slice(i, i + seatsPerRow);
      rows.push(
        <View key={i} style={styles.seatRow}>
          {rowSeats.map((seat) => (
            <TouchableOpacity
              key={seat.id}
              style={[
                styles.seat,
                { backgroundColor: getSeatColor(seat) }
              ]}
              onPress={() => onSeatPress(seat)}
            >
              <Text style={styles.seatText}>{seat.id}</Text>
            </TouchableOpacity>
          ))}
        </View>
      );
    }
    return rows;
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>{chamber} Chamber</Text>
        <View style={styles.legend}>
          <View style={styles.legendItem}>
            <View style={[styles.legendColor, { backgroundColor: '#2563eb' }]} />
            <Text style={styles.legendText}>Democrat</Text>
          </View>
          <View style={styles.legendItem}>
            <View style={[styles.legendColor, { backgroundColor: '#dc2626' }]} />
            <Text style={styles.legendText}>Republican</Text>
          </View>
          <View style={styles.legendItem}>
            <View style={[styles.legendColor, { backgroundColor: '#9ca3af' }]} />
            <Text style={styles.legendText}>Vacant</Text>
          </View>
        </View>
      </View>
      
      <View style={styles.chamberFloor}>
        <Text style={styles.podiumLabel}>Speaker's Podium</Text>
        <View style={styles.podium} />
        <View style={styles.seatsContainer}>
          {renderSeatGrid()}
        </View>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  header: {
    backgroundColor: '#ffffff',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#e5e7eb',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: 12,
  },
  legend: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  legendItem: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  legendColor: {
    width: 16,
    height: 16,
    borderRadius: 8,
    marginRight: 6,
  },
  legendText: {
    fontSize: 12,
    color: '#6b7280',
  },
  chamberFloor: {
    padding: 20,
    alignItems: 'center',
  },
  podiumLabel: {
    fontSize: 14,
    color: '#6b7280',
    marginBottom: 8,
  },
  podium: {
    width: 120,
    height: 40,
    backgroundColor: '#8b5cf6',
    borderRadius: 20,
    marginBottom: 30,
  },
  seatsContainer: {
    alignItems: 'center',
  },
  seatRow: {
    flexDirection: 'row',
    marginBottom: 8,
  },
  seat: {
    width: 32,
    height: 32,
    borderRadius: 16,
    marginHorizontal: 4,
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.2,
    shadowRadius: 2,
    elevation: 2,
  },
  seatText: {
    color: '#ffffff',
    fontSize: 10,
    fontWeight: 'bold',
  },
});