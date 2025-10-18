'use client'

interface IdeaCardProps {
  symbol: string
  action: 'BUY' | 'SELL' | 'HOLD'
  entry: number
  stop: number
  target: number
  thesis: string
  confidence: number
}

export default function IdeaCard({
  symbol,
  action,
  entry,
  stop,
  target,
  thesis,
  confidence,
}: IdeaCardProps) {
  const actionColor = {
    BUY: 'text-green-600 bg-green-100',
    SELL: 'text-red-600 bg-red-100',
    HOLD: 'text-gray-600 bg-gray-100',
  }[action]

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-4">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-2xl font-bold">{symbol}</h3>
          <span className={`inline-block px-3 py-1 rounded-full text-sm font-semibold ${actionColor}`}>
            {action}
          </span>
        </div>
        <div className="text-right">
          <p className="text-sm text-gray-600">Confidence</p>
          <p className="text-xl font-bold">{(confidence * 100).toFixed(0)}%</p>
        </div>
      </div>
      
      <div className="grid grid-cols-3 gap-4 mb-4">
        <div>
          <p className="text-sm text-gray-600">Entry</p>
          <p className="font-semibold">${entry.toFixed(2)}</p>
        </div>
        <div>
          <p className="text-sm text-gray-600">Stop</p>
          <p className="font-semibold">${stop.toFixed(2)}</p>
        </div>
        <div>
          <p className="text-sm text-gray-600">Target</p>
          <p className="font-semibold">${target.toFixed(2)}</p>
        </div>
      </div>
      
      <div>
        <p className="text-sm font-semibold text-gray-700 mb-2">Thesis</p>
        <p className="text-sm text-gray-600">{thesis}</p>
      </div>
    </div>
  )
}

