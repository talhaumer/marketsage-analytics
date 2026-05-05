import { useState } from 'react'
import { Loader2 } from 'lucide-react'
import { PriceChart } from './PriceChart'
import { TechnicalChart } from './TechnicalChart'
import { VolumeChart } from './VolumeChart'
import { SectorChart } from './SectorChart'

const TABS = ['Price', 'RSI', 'Volume', 'Sector']

export function ChartPanel({ chartData, loading, error }) {
  const [activeTab, setActiveTab] = useState('Price')

  if (!chartData && !loading) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <p className="text-sm text-slate-400">Add symbols to see charts</p>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full">
      <div className="flex gap-0.5 p-1 bg-slate-100 rounded-lg w-fit mb-3 flex-shrink-0">
        {TABS.map((tab) => (
          <button
            key={tab}
            type="button"
            onClick={() => setActiveTab(tab)}
            className={`px-3 py-1 text-xs rounded-md transition-colors ${
              activeTab === tab
                ? 'bg-white text-slate-800 font-medium shadow-sm'
                : 'text-slate-500 hover:text-slate-700'
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      <div className="flex-1 min-h-0">
        {loading ? (
          <div className="flex items-center justify-center h-full text-slate-400 text-sm gap-2">
            <Loader2 size={15} className="animate-spin" />
            Loading chart data…
          </div>
        ) : error ? (
          <div className="flex items-center justify-center h-full text-red-400 text-sm">
            Chart data unavailable
          </div>
        ) : (
          <>
            {activeTab === 'Price' && <PriceChart data={chartData} />}
            {activeTab === 'RSI' && <TechnicalChart data={chartData} />}
            {activeTab === 'Volume' && <VolumeChart data={chartData} />}
            {activeTab === 'Sector' && <SectorChart data={chartData} />}
          </>
        )}
      </div>
    </div>
  )
}
