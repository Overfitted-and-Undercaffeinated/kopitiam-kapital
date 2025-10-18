export default function EODReport() {
  return (
    <div className="container mx-auto p-8">
      <h1 className="text-3xl font-bold mb-6">End-of-Day Report</h1>
      <div className="bg-white p-6 rounded-lg shadow mb-6">
        <h2 className="text-2xl font-semibold mb-4">Market Summary</h2>
        <p className="text-gray-600">No report generated yet.</p>
      </div>
      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-2xl font-semibold mb-4">Portfolio Performance</h2>
        <p className="text-gray-600">No positions tracked yet.</p>
      </div>
    </div>
  )
}

