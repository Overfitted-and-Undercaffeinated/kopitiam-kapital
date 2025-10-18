import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

interface RecommendationSheetProps {
  symbol: string;
  action: 'BUY' | 'SELL' | 'HOLD';
  entry: number;
  stop: number;
  target: number;
  thesis: string;
  confidence: number;
}

export default function RecommendationSheet({
  symbol,
  action,
  entry,
  stop,
  target,
  thesis,
  confidence,
}: RecommendationSheetProps) {
  const actionColor = {
    BUY: '#10B981',
    SELL: '#EF4444',
    HOLD: '#6B7280',
  }[action];

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.symbol}>{symbol}</Text>
        <View style={[styles.actionBadge, { backgroundColor: actionColor }]}>
          <Text style={styles.actionText}>{action}</Text>
        </View>
      </View>
      
      <View style={styles.priceGrid}>
        <View style={styles.priceItem}>
          <Text style={styles.priceLabel}>Entry</Text>
          <Text style={styles.priceValue}>${entry.toFixed(2)}</Text>
        </View>
        <View style={styles.priceItem}>
          <Text style={styles.priceLabel}>Stop</Text>
          <Text style={styles.priceValue}>${stop.toFixed(2)}</Text>
        </View>
        <View style={styles.priceItem}>
          <Text style={styles.priceLabel}>Target</Text>
          <Text style={styles.priceValue}>${target.toFixed(2)}</Text>
        </View>
      </View>
      
      <View style={styles.thesisSection}>
        <Text style={styles.thesisLabel}>Thesis</Text>
        <Text style={styles.thesisText}>{thesis}</Text>
      </View>
      
      <View style={styles.confidenceSection}>
        <Text style={styles.confidenceLabel}>Confidence</Text>
        <Text style={styles.confidenceValue}>{(confidence * 100).toFixed(0)}%</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 20,
    marginVertical: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  symbol: {
    fontSize: 24,
    fontWeight: 'bold',
  },
  actionBadge: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
  },
  actionText: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 14,
  },
  priceGrid: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 16,
  },
  priceItem: {
    flex: 1,
  },
  priceLabel: {
    fontSize: 12,
    color: '#6B7280',
    marginBottom: 4,
  },
  priceValue: {
    fontSize: 16,
    fontWeight: '600',
  },
  thesisSection: {
    marginBottom: 16,
  },
  thesisLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#374151',
    marginBottom: 8,
  },
  thesisText: {
    fontSize: 14,
    color: '#6B7280',
    lineHeight: 20,
  },
  confidenceSection: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  confidenceLabel: {
    fontSize: 14,
    color: '#6B7280',
  },
  confidenceValue: {
    fontSize: 18,
    fontWeight: 'bold',
  },
});

