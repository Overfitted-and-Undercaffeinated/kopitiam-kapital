import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

interface AlertCardProps {
  title: string;
  message: string;
  type: 'info' | 'warning' | 'success' | 'error';
}

export default function AlertCard({ title, message, type }: AlertCardProps) {
  const borderColor = {
    info: '#3B82F6',
    warning: '#F59E0B',
    success: '#10B981',
    error: '#EF4444',
  }[type];

  const backgroundColor = {
    info: '#DBEAFE',
    warning: '#FEF3C7',
    success: '#D1FAE5',
    error: '#FEE2E2',
  }[type];

  return (
    <View style={[styles.container, { borderLeftColor: borderColor, backgroundColor }]}>
      <Text style={styles.title}>{title}</Text>
      <Text style={styles.message}>{message}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    borderLeftWidth: 4,
    padding: 16,
    marginVertical: 8,
    borderRadius: 8,
  },
  title: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  message: {
    fontSize: 14,
    color: '#4B5563',
  },
});

