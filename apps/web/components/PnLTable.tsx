'use client'

interface Position {
  symbol: string
  qty: number
  avgPrice: number
  currentPrice: number
  pnl: number
  pnlPct: number
}

interface PnLTableProps {
  positions: Position[]
}

export default function PnLTable({ positions }: PnLTableProps) {
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full bg-white rounded-lg shadow">
        <thead className="bg-gray-100">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Symbol
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Qty
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Avg Price
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Current
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              P&L
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              P&L %
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200">
          {positions.map((position, idx) => (
            <tr key={idx}>
              <td className="px-6 py-4 whitespace-nowrap font-semibold">
                {position.symbol}
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                {position.qty}
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                ${position.avgPrice.toFixed(2)}
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                ${position.currentPrice.toFixed(2)}
              </td>
              <td className={`px-6 py-4 whitespace-nowrap font-semibold ${
                position.pnl >= 0 ? 'text-green-600' : 'text-red-600'
              }`}>
                ${position.pnl.toFixed(2)}
              </td>
              <td className={`px-6 py-4 whitespace-nowrap font-semibold ${
                position.pnlPct >= 0 ? 'text-green-600' : 'text-red-600'
              }`}>
                {position.pnlPct.toFixed(2)}%
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

