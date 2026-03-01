import React from 'react';
import { View, Text, StyleSheet, Dimensions } from 'react-native';

interface ChamberVisualizationProps {
  chamber: 'senate' | 'assembly';
  democratCount: number;
  republicanCount: number;
  totalSeats: number;
}

export function ChamberVisualization({ 
  chamber, 
  democratCount, 
  republicanCount, 
  totalSeats 
}: ChamberVisualizationProps) {
  const screenWidth = Dimensions.get('window').width;
  const seatSize = 12;
  const spacing = 4;
  
  const createGridSeats = () => {
    const seats = [];
    const cols = chamber === 'senate' ? 8 : 10;
    const rows = Math.ceil(totalSeats / cols);
    
    for (let row = 0; row < rows; row++) {
      for (let col = 0; col < cols && seats.length < totalSeats; col++) {
        const seatIndex: number = seats.length;
        const isRepublican: boolean = seatIndex >= democratCount;
        
        seats.push({
          row,
          col,
          party: isRepublican ? 'republican' : 'democrat',
          key: `seat-${seatIndex}`
        });
      }
    }
    return seats;
  };

  const seats = createGridSeats();
  const cols = chamber === 'senate' ? 8 : 10;
  const gridWidth = cols * (seatSize + spacing) - spacing;

  return (
    <View style={styles.container}>
      <Text style={[styles.chamberTitle, { color: '#1e40af' }]}>
        {chamber === 'senate' ? 'NJ SENATE' : 'NJ ASSEMBLY'}
      </Text>
      
      <View style={[styles.visualization, { width: gridWidth }]}>
        {seats.map(seat => (
          <View
            key={seat.key}
            style={[
              styles.seat,
              {
                left: seat.col * (seatSize + spacing),
                top: seat.row * (seatSize + spacing),
                backgroundColor: seat.party === 'democrat' ? '#1e40af' : '#dc2626',
                width: seatSize,
                height: seatSize
              }
            ]}
          />
        ))}
      </View>
      
      <View style={styles.legend}>
        <View style={styles.legendItem}>
          <View style={[styles.legendDot, { backgroundColor: '#1e40af' }]} />
          <Text style={styles.legendText}>Democrats ({democratCount})</Text>
        </View>
        <View style={styles.legendItem}>
          <View style={[styles.legendDot, { backgroundColor: '#dc2626' }]} />
          <Text style={styles.legendText}>Republicans ({republicanCount})</Text>
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
    paddingVertical: 20,
    backgroundColor: '#f8fafc'
  },
  chamberTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 20,
  },
  visualization: {
    position: 'relative',
    height: 120,
    backgroundColor: '#ffffff',
    borderRadius: 8,
    padding: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3
  },
  seat: {
    position: 'absolute',
    borderRadius: 2,
  },
  legend: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    width: '100%',
    marginTop: 15,
  },
  legendItem: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  legendDot: {
    width: 12,
    height: 12,
    borderRadius: 6,
    marginRight: 8,
  },
  legendText: {
    fontSize: 14,
    color: '#374151',
  },
});