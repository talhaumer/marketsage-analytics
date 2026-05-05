import { useState, useEffect } from 'react'
import { useLocation } from 'react-router-dom'
import { Loader2 } from 'lucide-react'
import { SymbolInput } from './SymbolInput'

const ANALYSIS_TYPES = [
  'comprehensive', 'technical', 'risk', 'sentiment', 'portfolio', 'crypto', 'quick',
]
const TIMEFRAMES = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y']
const RISK_LEVELS = ['conservative', 'moderate', 'aggressive']

export function QueryPanel({ onRun, loading, onSymbolsChange, onTimeframeChange }) {
  const location = useLocation()
  const replay = location.state?.replay

  const [question, setQuestion] = useState(replay?.question || '')
  const [symbols, setSymbols] = useState(replay?.symbols || [])
  const [analysisType, setAnalysisType] = useState(replay?.analysis_type || 'comprehensive')
  const [timeframe, setTimeframe] = useState('1y')
  const [risk, setRisk] = useState('moderate')
  const [didAutoRun, setDidAutoRun] = useState(false)

  useEffect(() => {
    onSymbolsChange?.(symbols)
  }, [symbols])

  useEffect(() => {
    onTimeframeChange?.(timeframe)
  }, [timeframe])

  // Auto-submit when arriving from History replay
  useEffect(() => {
    if (replay && !didAutoRun && question) {
      setDidAutoRun(true)
      onRun({ question, symbols, analysis_type: analysisType, timeframe, risk_tolerance: risk })
    }
  }, [])

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!question.trim() || loading) return
    onRun({ question, symbols, analysis_type: analysisType, timeframe, risk_tolerance: risk })
  }

  return (
    <form onSubmit={handleSubmit} className="p-4 border-b border-slate-100">
      <div className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-3">
        Query
      </div>

      <textarea
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        maxLength={1000}
        rows={3}
        placeholder="What's the outlook for AAPL this quarter?"
        className="w-full resize-none bg-slate-50 border border-slate-200 rounded-md p-2.5 text-sm text-slate-700 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent mb-2.5 transition-shadow"
      />

      <div className="mb-2.5">
        <div className="text-xs text-slate-400 mb-1">Symbols</div>
        <SymbolInput symbols={symbols} onChange={setSymbols} />
      </div>

      <div className="flex flex-wrap gap-1.5 mb-2.5">
        {ANALYSIS_TYPES.map((t) => (
          <button
            key={t}
            type="button"
            onClick={() => setAnalysisType(t)}
            className={`px-2.5 py-1 rounded text-xs font-medium transition-colors ${
              analysisType === t
                ? 'bg-indigo-600 text-white'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            }`}
          >
            {t.charAt(0).toUpperCase() + t.slice(1)}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-2 gap-2 mb-3">
        <div>
          <div className="text-xs text-slate-400 mb-1">Timeframe</div>
          <select
            value={timeframe}
            onChange={(e) => setTimeframe(e.target.value)}
            className="w-full border border-slate-200 rounded-md px-2 py-1.5 text-xs text-slate-700 bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            {TIMEFRAMES.map((t) => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
        </div>
        <div>
          <div className="text-xs text-slate-400 mb-1">Risk Tolerance</div>
          <select
            value={risk}
            onChange={(e) => setRisk(e.target.value)}
            className="w-full border border-slate-200 rounded-md px-2 py-1.5 text-xs text-slate-700 bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            {RISK_LEVELS.map((r) => (
              <option key={r} value={r}>{r.charAt(0).toUpperCase() + r.slice(1)}</option>
            ))}
          </select>
        </div>
      </div>

      <button
        type="submit"
        disabled={loading || !question.trim()}
        className="w-full bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg py-2.5 text-sm font-semibold flex items-center justify-center gap-2 transition-colors"
      >
        {loading ? (
          <>
            <Loader2 size={14} className="animate-spin" />
            Analyzing…
          </>
        ) : (
          'Run Analysis →'
        )}
      </button>
    </form>
  )
}
