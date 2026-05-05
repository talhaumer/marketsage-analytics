import { useEffect, useState, useRef } from 'react'
import { AlertTriangle } from 'lucide-react'

const AGENT_LABELS = {
  market_research: '📰 Market Research',
  technical_analysis: '📊 Technical Analysis',
  risk_assessment: '⚠️ Risk Assessment',
  sentiment_analysis: '💬 Sentiment Analysis',
  portfolio_analysis: '📈 Portfolio Analysis',
  sector_analysis: '🏭 Sector Analysis',
  crypto_analysis: '₿ Crypto Analysis',
}

export function AnalysisResult({ result }) {
  const [displayed, setDisplayed] = useState('')
  const [expanded, setExpanded] = useState({})
  const intervalRef = useRef(null)

  const fullText = result?.data?.final_analysis || ''

  useEffect(() => {
    clearInterval(intervalRef.current)
    setDisplayed('')
    if (!fullText) return

    let idx = 0
    intervalRef.current = setInterval(() => {
      idx = Math.min(idx + 3, fullText.length)
      setDisplayed(fullText.slice(0, idx))
      if (idx >= fullText.length) clearInterval(intervalRef.current)
    }, 15)

    return () => clearInterval(intervalRef.current)
  }, [fullText])

  const individual = result?.data?.individual_analyses || {}
  const agentEntries = Object.entries(AGENT_LABELS).filter(([k]) => individual[k])

  return (
    <div>
      {result?.error && (
        <div className="flex items-start gap-2 bg-amber-50 border border-amber-200 rounded-md p-3 mb-3 text-xs text-amber-800">
          <AlertTriangle size={13} className="shrink-0 mt-0.5" />
          <span>Some agents reported issues: {result.error}</span>
        </div>
      )}

      <div className="text-sm text-slate-700 leading-relaxed whitespace-pre-wrap mb-4">
        {displayed}
        {displayed.length < fullText.length && (
          <span className="inline-block w-0.5 h-4 bg-indigo-500 animate-pulse ml-0.5 align-middle" />
        )}
      </div>

      {agentEntries.length > 0 && (
        <div className="border border-slate-200 rounded-md overflow-hidden">
          <div className="px-3 py-2 bg-slate-50 border-b border-slate-200 text-xs font-semibold text-slate-500 uppercase tracking-wide">
            Agent Outputs
          </div>
          {agentEntries.map(([key, label]) => (
            <div key={key} className="border-b border-slate-100 last:border-0">
              <button
                type="button"
                onClick={() => setExpanded((p) => ({ ...p, [key]: !p[key] }))}
                className="w-full flex justify-between items-center px-3 py-2.5 text-xs font-medium text-slate-600 hover:bg-slate-50 transition-colors text-left"
              >
                {label}
                <span className="text-slate-400 ml-2 flex-shrink-0">{expanded[key] ? '▾' : '›'}</span>
              </button>
              {expanded[key] && (
                <div className="px-3 pb-3 text-xs text-slate-600 leading-relaxed whitespace-pre-wrap bg-slate-50 border-t border-slate-100">
                  {individual[key]}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
