import { useState } from 'react'
import { Plus, Trash2, Loader2 } from 'lucide-react'
import { AllocationChart } from '../components/charts/AllocationChart'
import client from '../api/client'

export function Portfolio() {
  const [rows, setRows] = useState([{ symbol: '', weight: 100 }])
  const [risk, setRisk] = useState('moderate')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const totalWeight = rows.reduce((s, r) => s + Number(r.weight), 0)
  const weightsValid = Math.abs(totalWeight - 100) < 0.5
  const symbolsValid = rows.every((r) => /^[A-Z0-9.]{1,10}$/.test(r.symbol.trim()))
  const canSubmit = weightsValid && symbolsValid && rows.length >= 1 && !loading

  const updateRow = (i, field, value) =>
    setRows((prev) => prev.map((r, idx) => (idx === i ? { ...r, [field]: value } : r)))

  const addRow = () =>
    setRows((prev) => [...prev, { symbol: '', weight: 0 }])

  const removeRow = (i) =>
    setRows((prev) => prev.filter((_, idx) => idx !== i))

  const handleSubmit = async () => {
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const symbols = rows.map((r) => r.symbol.trim().toUpperCase())
      const weights = rows.map((r) => parseFloat((Number(r.weight) / 100).toFixed(4)))
      const { data } = await client.post('/portfolio', {
        symbols,
        weights,
        risk_tolerance: risk,
      })
      if (data.success) setResult(data)
      else setError(data.error || 'Portfolio analysis failed')
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        err.message ||
        'Backend unreachable — make sure python main.py is running.',
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-6 max-w-5xl mx-auto w-full">
      <h1 className="text-lg font-bold text-slate-900 mb-5">Portfolio Analyzer</h1>

      <div className="grid grid-cols-[360px_1fr] gap-6 items-start">
        {/* Builder */}
        <div className="bg-white border border-slate-200 rounded-lg p-4">
          <div className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-3">
            Build Portfolio
          </div>

          <div className="flex flex-col gap-2 mb-3">
            {rows.map((row, i) => (
              <div key={i} className="flex items-center gap-2">
                <input
                  value={row.symbol}
                  onChange={(e) => updateRow(i, 'symbol', e.target.value.toUpperCase())}
                  placeholder="AAPL"
                  maxLength={10}
                  className="w-20 border border-slate-200 rounded px-2 py-1 text-xs text-slate-700 uppercase focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={row.weight}
                  onChange={(e) => updateRow(i, 'weight', e.target.value)}
                  className="flex-1 accent-indigo-600"
                />
                <input
                  type="number"
                  min="0"
                  max="100"
                  value={row.weight}
                  onChange={(e) => updateRow(i, 'weight', e.target.value)}
                  className="w-14 border border-slate-200 rounded px-2 py-1 text-xs text-center focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
                <span className="text-xs text-slate-400">%</span>
                {rows.length > 1 && (
                  <button
                    type="button"
                    onClick={() => removeRow(i)}
                    className="text-slate-300 hover:text-red-400 transition-colors"
                    aria-label="Remove symbol"
                  >
                    <Trash2 size={13} />
                  </button>
                )}
              </div>
            ))}
          </div>

          <button
            type="button"
            onClick={addRow}
            disabled={rows.length >= 50}
            className="flex items-center gap-1 text-xs text-indigo-600 hover:text-indigo-800 transition-colors mb-4 disabled:opacity-40"
          >
            <Plus size={12} />
            Add symbol
          </button>

          <div
            className={`text-xs mb-3 font-medium ${
              weightsValid ? 'text-emerald-600' : 'text-amber-600'
            }`}
          >
            Total: {totalWeight.toFixed(1)}%{' '}
            {weightsValid ? '✓ ready' : '— must equal 100%'}
          </div>

          <div className="mb-3">
            <div className="text-xs text-slate-400 mb-1">Risk Tolerance</div>
            <select
              value={risk}
              onChange={(e) => setRisk(e.target.value)}
              className="w-full border border-slate-200 rounded px-2 py-1.5 text-xs focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="conservative">Conservative</option>
              <option value="moderate">Moderate</option>
              <option value="aggressive">Aggressive</option>
            </select>
          </div>

          <button
            type="button"
            onClick={handleSubmit}
            disabled={!canSubmit}
            className="w-full bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg py-2 text-sm font-semibold flex items-center justify-center gap-2 transition-colors"
          >
            {loading ? (
              <>
                <Loader2 size={14} className="animate-spin" />
                Analyzing…
              </>
            ) : (
              'Analyze Portfolio →'
            )}
          </button>

          {error && (
            <div className="mt-2 text-xs text-red-600 bg-red-50 border border-red-200 rounded p-2">
              {error}
            </div>
          )}
        </div>

        {/* Result */}
        <div>
          {result ? (
            <div className="flex flex-col gap-4">
              <div className="bg-white border border-slate-200 rounded-lg p-4">
                <div className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">
                  Allocation
                </div>
                <div className="h-52">
                  <AllocationChart
                    symbols={rows.map((r) => r.symbol.toUpperCase())}
                    weights={rows.map((r) => Number(r.weight))}
                  />
                </div>
              </div>
              <div className="bg-white border border-slate-200 rounded-lg p-4">
                <div className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">
                  AI Analysis
                </div>
                <div className="text-sm text-slate-700 leading-relaxed whitespace-pre-wrap">
                  {result.data?.final_analysis}
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-white border border-slate-200 rounded-lg p-10 text-center text-slate-400 text-sm">
              Build your portfolio on the left and click Analyze to see results.
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
