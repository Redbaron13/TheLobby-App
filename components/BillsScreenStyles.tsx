import { StyleSheet } from 'react-native';

export const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  header: {
    padding: 20,
    backgroundColor: '#1e40af',
    borderBottomWidth: 1,
    borderBottomColor: '#d97706',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#1e293b',
    marginBottom: 16,
  },
  syncButton: {
    backgroundColor: '#d97706',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 8,
    alignSelf: 'flex-start',
    marginBottom: 16,
  },
  syncButtonText: {
    color: '#ffffff',
    fontWeight: '600',
    fontSize: 14,
  },
  searchInput: {
    backgroundColor: '#3b82f6',
    borderRadius: 12,
    paddingHorizontal: 16,
    paddingVertical: 12,
    fontSize: 16,
    marginBottom: 16,
    color: '#ffffff',
  },
  resultCount: {
    fontSize: 14,
    color: '#64748b',
    marginBottom: 12,
    paddingHorizontal: 16,
  },
  filterContainer: {
    flexDirection: 'row',
    gap: 8,
  },
  filterButton: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    backgroundColor: '#64748b',
  },
  activeFilter: {
    backgroundColor: '#d97706',
  },
  filterText: {
    fontSize: 14,
    color: '#ffffff',
    fontWeight: '500',
  },
  activeFilterText: {
    color: '#ffffff',
  },
  content: {
    padding: 16,
  },
  loadingText: {
    textAlign: 'center',
    fontSize: 16,
    color: '#64748b',
    marginTop: 40,
  },
  noDataText: {
    textAlign: 'center',
    fontSize: 16,
    color: '#64748b',
    marginTop: 40,
  },
  errorText: {
    textAlign: 'center',
    fontSize: 16,
    color: '#dc2626',
    marginHorizontal: 16,
    marginBottom: 16,
  },
  retryButton: {
    alignSelf: 'center',
    backgroundColor: '#1e40af',
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderRadius: 8,
  },
  retryButtonText: {
    color: '#ffffff',
    fontWeight: '600',
  },
  billsList: {
    paddingHorizontal: 16,
  },
  emptyStateText: {
    textAlign: 'center',
    color: '#64748b',
    marginTop: 24,
  },
  actionMessage: {
    textAlign: 'center',
    color: '#059669',
    marginBottom: 12,
  },
  billCard: {
    backgroundColor: '#ffffff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
    borderLeftWidth: 4,
    borderLeftColor: '#1e40af',
  },
  billHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  billType: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
  },
  billNumber: {
    color: '#1e293b',
    fontWeight: 'bold',
    fontSize: 14,
  },
  billStatus: {
    fontSize: 14,
    color: '#d97706',
    fontWeight: '600',
  },
  billTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1e40af',
    marginBottom: 8,
    lineHeight: 24,
  },
  billSponsor: {
    fontSize: 14,
    color: '#64748b',
    marginBottom: 4,
  },
  billCommittee: {
    fontSize: 14,
    color: '#1e40af',
    marginBottom: 4,
    fontWeight: '500',
  },
  billDate: {
    fontSize: 14,
    color: '#64748b',
    marginBottom: 8,
  },
  billSynopsis: {
    fontSize: 14,
    color: '#475569',
    lineHeight: 20,
    fontStyle: 'italic',
  },
  saveButton: {
    marginTop: 12,
    backgroundColor: '#059669',
    borderRadius: 8,
    paddingVertical: 10,
    alignItems: 'center',
  },
  saveButtonText: {
    color: '#ffffff',
    fontWeight: '600',
  },
});
