'use client';

import { useState } from 'react';
import BacktestChart from '@/components/BacktestChart';

/**
 * Example: How to use BacktestChart with API data
 * 
 * This shows how to fetch backtest data from the API
 * and display it using the BacktestChart component
 */

export default function BacktestExample() {
  const [loading, setLoading] = useState(false);
  const [backtestData, setBacktestData] = useState<any>(null);

  const runBacktest = async () => {
    setLoading(true);
    
    try {
      // Call your API endpoint
      const response = await fetch(
        '/api/assistant/chat?message=backtest mean reversion on AAPL&user_id=test-user',
        {
          method: 'POST',
        }
      );

      const data = await response.json();

      // The API returns:
      // {
      //   short_response: string,
      //   detailed_response: string,
      //   metadata: {
      //     chart_data: [
      //       {
      //         symbol: "AAPL",
      //         equity_curve: [...],
      //       }
      //     ],
      //     ...
      //   }
      // }

      setBacktestData(data);
    } catch (error) {
      console.error('Backtest error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-white mb-8">Backtest Demo</h1>

        {/* Run Backtest Button */}
        <button
          onClick={runBacktest}
          disabled={loading}
          className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-semibold disabled:opacity-50 disabled:cursor-not-allowed mb-8"
        >
          {loading ? 'Running Backtest...' : 'Run Mean Reversion on AAPL'}
        </button>

        {/* Display Charts */}
        {backtestData?.metadata?.chart_data?.map((chartData: any, index: number) => (
          <div key={index} className="mb-8">
            <BacktestChart
              symbol={chartData.symbol}
              strategyName={backtestData.metadata.strategy_name}
              equityCurve={chartData.equity_curve}
              drawdownSeries={backtestData.visuals?.drawdown_series}
              metrics={backtestData.metadata.metrics}
            />
          </div>
        ))}

        {/* Response Text */}
        {backtestData && (
          <div className="bg-white dark:bg-slate-800 p-6 rounded-lg shadow mt-8">
            <h2 className="text-xl font-bold mb-4">Analysis</h2>
            <div
              className="prose dark:prose-invert"
              dangerouslySetInnerHTML={{ __html: backtestData.detailed_response }}
            />
          </div>
        )}
      </div>
    </div>
  );
}

