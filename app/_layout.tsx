import { Stack } from 'expo-router';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { useEffect, useState } from 'react';
import { useRouter, usePathname } from 'expo-router';
import { loadSupabaseConfig } from '@/app/lib/supabase';

function TopNavigation() {
  const [isOpen, setIsOpen] = useState(false);
  const router = useRouter();
  const pathname = usePathname();

  const menuItems = [
    { name: 'Home', path: '/' },
    { name: 'Bills & Legislation', path: '/bills' },
    { name: 'Senate', path: '/senate' },
    { name: 'Assembly', path: '/assembly' },
    { name: 'All Legislators', path: '/legislators' },
    { name: 'Find Your Legislator', path: '/find-legislator' },
    { name: 'Profile', path: '/profile' },
    { name: 'Supabase Setup', path: '/setup' },
  ];

  const getCurrentTitle = () => {
    if (pathname === '/') return 'NJ Legislature';
    if (pathname === '/bills') return 'Bills & Legislation';
    if (pathname === '/senate') return 'Senate';
    if (pathname === '/assembly') return 'Assembly';
    if (pathname === '/legislators') return 'All Legislators';
    if (pathname === '/find-legislator') return 'Find Your Legislator';
    if (pathname === '/profile') return 'Profile';
    if (pathname === '/setup') return 'Supabase Setup';
    return 'NJ Legislature';
  };

  return (
    <View style={styles.topNav}>
      <Text style={styles.title}>{getCurrentTitle()}</Text>
      <TouchableOpacity 
        style={styles.menuButton}
        onPress={() => setIsOpen(!isOpen)}
      >
        <Text style={styles.menuIcon}>☰</Text>
      </TouchableOpacity>
      
      {isOpen && (
        <View style={styles.dropdown}>
          {menuItems.map((item) => (
            <TouchableOpacity
              key={item.path}
              style={[styles.menuItem, pathname === item.path && styles.activeMenuItem]}
              onPress={() => {
                router.push(item.path);
                setIsOpen(false);
              }}
            >
              <Text style={[styles.menuText, pathname === item.path && styles.activeMenuText]}>
                {item.name}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      )}
    </View>
  );
}

export default function RootLayout() {
  useEffect(() => {
    loadSupabaseConfig();
  }, []);

  return (
    <View style={{ flex: 1 }}>
      <TopNavigation />
      <Stack screenOptions={{ headerShown: false }}>
        <Stack.Screen name="index" />
        <Stack.Screen name="bills" />
        <Stack.Screen name="legislators" />
        <Stack.Screen name="find-legislator" />
        <Stack.Screen name="senate" />
        <Stack.Screen name="assembly" />
        <Stack.Screen name="profile" />
        <Stack.Screen name="setup" />
      </Stack>
    </View>
  );
}

const styles = StyleSheet.create({
  topNav: {
    backgroundColor: '#0f172a',
    paddingTop: 50,
    paddingHorizontal: 16,
    paddingBottom: 12,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    position: 'relative',
    zIndex: 1000,
  },
  title: {
    color: '#ffffff',
    fontSize: 20,
    fontWeight: 'bold',
  },
  menuButton: {
    padding: 8,
  },
  menuIcon: {
    color: '#ffffff',
    fontSize: 24,
  },
  dropdown: {
    position: 'absolute',
    top: '100%',
    right: 16,
    backgroundColor: '#1e293b',
    borderRadius: 8,
    minWidth: 200,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5,
  },
  menuItem: {
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#334155',
  },
  activeMenuItem: {
    backgroundColor: '#059669',
  },
  menuText: {
    color: '#e2e8f0',
    fontSize: 16,
  },
  activeMenuText: {
    color: '#ffffff',
    fontWeight: '600',
  },
});
