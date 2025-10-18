'use client';

import React from 'react';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';

interface EquityCurvePoint {
  date: string;
  equity: number;
  trade_pnl: number;
}

interface DrawdownPoint {
  date: string;
  drawdown: number;
}

interface BacktestChartProps {
  symbol: string;
  strategyName: string;
  equityCurve: EquityCurvePoint[];
  drawdownSeries?: DrawdownPoint[];
  metrics?: {
    total_return: number;
    total_return_pct: number;
    win_rate: number;
    sharpe_ratio: number;
    max_drawdown: number;
    num_trades: number;
    winning_trades: number;
    losing_trades: number;
    profit_factor: number;
    avg_win: number;
    avg_loss: number;
  };
}

export default function BacktestChart({
  symbol,
  strategyName,
  equityCurve,
  drawdownSeries,
  metrics,
}: BacktestChartProps) {
  // Format currency
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  // Format percentage
  const formatPercent = (value: number) => {
    return `${(value * 100).toFixed(2)}%`;
  };

  // Format date for display
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  // Get starting equity for reference line
  const startingEquity = equityCurve.length > 0 ? equityCurve[0].equity : 100000;

  // Calculate min/max equity for Y-axis scaling
  const equityValues = equityCurve.map(p => p.equity);
  const minEquity = Math.min(...equityValues);
  const maxEquity = Math.max(...equityValues);
  
  // Add 5% padding on top and bottom for better visualization
  const range = maxEquity - minEquity;
  const padding = range * 0.05;
  const yAxisMin = Math.floor(minEquity - padding);
  const yAxisMax = Math.ceil(maxEquity + padding);

  // Transform equity curve data for recharts
  const equityData = equityCurve.map((point) => ({
    date: formatDate(point.date),
    fullDate: point.date,
    equity: point.equity,
    startingEquity: startingEquity,
  }));

  // Transform drawdown data
  const drawdownData = drawdownSeries?.map((point) => ({
    date: formatDate(point.date),
    fullDate: point.date,
    drawdown: point.drawdown * 100, // Convert to percentage
  })) || [];

  return (
    <div className="w-full space-y-6 bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 p-6 rounded-xl shadow-lg">
      {/* Header */}
      <div className="text-center">
        <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100">
          {strategyName} - {symbol}
        </h2>
        <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">
          Backtest Performance Analysis
        </p>
      </div>

      {/* Equity Curve */}
      <div className="bg-white dark:bg-slate-800 p-4 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4 text-slate-900 dark:text-slate-100">
          Portfolio Value Over Time
        </h3>
        <ResponsiveContainer width="100%" height={400}>
          <AreaChart data={equityData}>
            <defs>
              <linearGradient id="colorEquity" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#2E86AB" stopOpacity={0.8} />
                <stop offset="95%" stopColor="#2E86AB" stopOpacity={0.1} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis
              dataKey="date"
              stroke="#6b7280"
              tick={{ fill: '#6b7280', fontSize: 12 }}
            />
            <YAxis
              stroke="#6b7280"
              tick={{ fill: '#6b7280', fontSize: 12 }}
              tickFormatter={formatCurrency}
              domain={[yAxisMin, yAxisMax]}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: 'rgba(255, 255, 255, 0.95)',
                border: '1px solid #e5e7eb',
                borderRadius: '8px',
                padding: '12px',
              }}
              formatter={(value: number) => [formatCurrency(value), 'Portfolio']}
              labelFormatter={(label) => `Date: ${label}`}
            />
            <Legend />
            <ReferenceLine
              y={startingEquity}
              stroke="#9ca3af"
              strokeDasharray="5 5"
              label="Starting Capital"
            />
            <Area
              type="monotone"
              dataKey="equity"
              stroke="#2E86AB"
              strokeWidth={2}
              fill="url(#colorEquity)"
              name="Portfolio Value"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Drawdown Chart */}
      {drawdownData.length > 0 && (
        <div className="bg-white dark:bg-slate-800 p-4 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4 text-slate-900 dark:text-slate-100">
            Drawdown
          </h3>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={drawdownData}>
              <defs>
                <linearGradient id="colorDrawdown" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#ef4444" stopOpacity={0.8} />
                  <stop offset="95%" stopColor="#ef4444" stopOpacity={0.1} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis
                dataKey="date"
                stroke="#6b7280"
                tick={{ fill: '#6b7280', fontSize: 12 }}
              />
              <YAxis
                stroke="#6b7280"
                tick={{ fill: '#6b7280', fontSize: 12 }}
                tickFormatter={(value) => `${value.toFixed(1)}%`}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'rgba(255, 255, 255, 0.95)',
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                  padding: '12px',
                }}
                formatter={(value: number) => [`${value.toFixed(2)}%`, 'Drawdown']}
              />
              <Area
                type="monotone"
                dataKey="drawdown"
                stroke="#dc2626"
                strokeWidth={2}
                fill="url(#colorDrawdown)"
                name="Drawdown"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Performance Metrics Grid */}
      {metrics && (
        <div className="bg-white dark:bg-slate-800 p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4 text-slate-900 dark:text-slate-100">
            Performance Metrics
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            <MetricCard
              label="Total Return"
              value={formatCurrency(metrics.total_return)}
              subValue={formatPercent(metrics.total_return_pct)}
              positive={metrics.total_return > 0}
            />
            <MetricCard
              label="Win Rate"
              value={formatPercent(metrics.win_rate)}
              subValue={`${metrics.winning_trades}W / ${metrics.losing_trades}L`}
            />
            <MetricCard
              label="Sharpe Ratio"
              value={metrics.sharpe_ratio.toFixed(2)}
              subValue={
                metrics.sharpe_ratio > 2
                  ? 'Excellent'
                  : metrics.sharpe_ratio > 1
                  ? 'Good'
                  : 'Needs Work'
              }
            />
            <MetricCard
              label="Max Drawdown"
              value={formatPercent(Math.abs(metrics.max_drawdown))}
              subValue="Peak to Trough"
              negative={true}
            />
            <MetricCard
              label="Profit Factor"
              value={metrics.profit_factor.toFixed(2)}
              subValue={metrics.profit_factor > 2 ? 'Strong' : 'Moderate'}
            />
            <MetricCard
              label="Total Trades"
              value={metrics.num_trades.toString()}
              subValue={`${metrics.winning_trades} wins`}
            />
            <MetricCard
              label="Avg Win"
              value={formatCurrency(metrics.avg_win)}
              positive={true}
            />
            <MetricCard
              label="Avg Loss"
              value={formatCurrency(Math.abs(metrics.avg_loss))}
              negative={true}
            />
          </div>
        </div>
      )}
    </div>
  );
}

interface MetricCardProps {
  label: string;
  value: string;
  subValue?: string;
  positive?: boolean;
  negative?: boolean;
}

function MetricCard({ label, value, subValue, positive, negative }: MetricCardProps) {
  const valueColor = positive
    ? 'text-green-600 dark:text-green-400'
    : negative
    ? 'text-red-600 dark:text-red-400'
    : 'text-slate-900 dark:text-slate-100';

  return (
    <div className="bg-slate-50 dark:bg-slate-700 p-4 rounded-lg">
      <p className="text-xs text-slate-600 dark:text-slate-400 font-medium mb-1">
        {label}
      </p>
      <p className={`text-xl font-bold ${valueColor}`}>{value}</p>
      {subValue && (
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">{subValue}</p>
      )}
    </div>
  );
}

