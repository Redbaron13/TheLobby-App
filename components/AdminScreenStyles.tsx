import { StyleSheet, Platform } from 'react-native';

export const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0f172a', // Slate 900
    padding: 16,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#f8fafc', // Slate 50
  },
  controlPanel: {
    backgroundColor: '#1e293b', // Slate 800
    padding: 16,
    borderRadius: 8,
    marginBottom: 20,
  },
  controlTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#e2e8f0', // Slate 200
    marginBottom: 12,
  },
  syncButton: {
    backgroundColor: '#059669', // Emerald 600
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 6,
    alignItems: 'center',
  },
  syncButtonText: {
    color: '#ffffff',
    fontWeight: '600',
    fontSize: 16,
  },
  filterContainer: {
    flexDirection: 'row',
    marginBottom: 12,
    flexWrap: 'wrap',
    gap: 8,
  },
  filterButton: {
    backgroundColor: '#334155', // Slate 700
    paddingVertical: 6,
    paddingHorizontal: 12,
    borderRadius: 16,
  },
  filterButtonActive: {
    backgroundColor: '#0ea5e9', // Sky 500
  },
  filterText: {
    color: '#e2e8f0',
    fontSize: 14,
  },
  filterTextActive: {
    color: '#ffffff',
    fontWeight: '600',
  },
  list: {
    flex: 1,
  },
  issueCard: {
    backgroundColor: '#1e293b', // Slate 800
    borderRadius: 8,
    padding: 16,
    marginBottom: 12,
    borderLeftWidth: 4,
    borderLeftColor: '#ef4444', // Red 500
  },
  issueHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  issueTable: {
    color: '#94a3b8', // Slate 400
    fontSize: 12,
    fontWeight: '600',
    textTransform: 'uppercase',
  },
  issueDate: {
    color: '#64748b', // Slate 500
    fontSize: 12,
  },
  issueType: {
    color: '#f8fafc', // Slate 50
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 4,
  },
  issueDetails: {
    color: '#cbd5e1', // Slate 300
    fontSize: 14,
    marginBottom: 8,
  },
  expandButton: {
    alignSelf: 'flex-start',
  },
  expandText: {
    color: '#38bdf8', // Sky 400
    fontSize: 12,
  },
  rawContainer: {
    marginTop: 8,
    backgroundColor: '#0f172a', // Slate 900
    padding: 8,
    borderRadius: 4,
  },
  rawText: {
    color: '#94a3b8', // Slate 400
    fontSize: 11,
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
  },
  emptyText: {
    color: '#94a3b8', // Slate 400
    textAlign: 'center',
    marginTop: 40,
    fontSize: 16,
  },
});
