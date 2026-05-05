import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { ExternalLink, Clock, BarChart2, Hash } from 'lucide-react'
import client from '../api/client'

const TYPE_COLORS = {
  comprehensive: 'bg-indigo-50 text-indigo-700 border-indigo-200',
  technical:     'bg-amber-50 text-amber-700 border-amber-200',
  risk:          'bg-red-50 text-red-700 border-red-200',
  sentiment:     'bg-purple-50 text-purple-700 border-purple-200',
  portfolio:     'bg-emerald-50 text-emerald-700 border-emerald-200',
  crypto:        'bg-pink-50 text-pink-700 border-pink-200',
  quick:         'bg-slate-50 text-slate-600 border-slate-200',
}

export function History() {
  const [history, setHistory] = useState([])
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const navigate = useNavigate()

  useEffect(() => {
    Promise.all([client.get('/history'), client.get('/stats')])
      .then(([h, s]) => {
        setHistory(h.data.history || [])
        setStats(s.data)
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  const handleReplay = (record) => {
    navigate('/', {
      state: {
        replay: {
          question: record.question,
          symbols: record.symbols,
          analysis_type: record.analysis_type,
        },
      },
    })
  }

  return (
    <div className="p-6 max-w-5xl mx-auto w-full">
      <h1 className="text-lg font-bold text-slate-900 mb-5">Query History</h1>

      {stats && (
        <div className="grid grid-cols-3 gap-4 mb-6">
          {[
            { icon: Hash, label: 'Total Queries', value: stats.total_queries, color: 'text-slate-900' },
            { icon: Clock, label: 'Avg Time', value: `${stats.average_processing_time}s`, color: 'text-slate-900' },
            {
              icon: BarChart2,
              label: 'Top Symbol',
              value: stats.most_analyzed_symbols[0]?.[0] || '—',
              color: 'text-indigo-600',
            },
          ].map(({ icon: Icon, label, value, color }) => (
            <div key={label} className="bg-white border border-slate-200 rounded-lg p-4">
              <div className="flex items-center gap-1.5 text-slate-400 text-xs mb-1.5">
                <Icon size={12} />
                {label}
              </div>
              <div className={`text-2xl font-bold ${color}`}>{value}</div>
            </div>
          ))}
        </div>
      )}

      <div className="bg-white border border-slate-200 rounded-lg overflow-hidden">
        <div className="grid grid-cols-[1fr_110px_120px_70px_80px] px-4 py-2.5 bg-slate-50 border-b border-slate-200 text-xs font-semibold text-slate-500 uppercase tracking-wide">
          <span>Question</span>
          <span>Symbols</span>
          <span>Type</span>
          <span>Time</span>
          <span />
        </div>

        {loading ? (
          <div className="text-center py-10 text-slate-400 text-sm">Loading…</div>
        ) : error ? (
          <div className="text-center py-10 text-red-400 text-sm">{error}</div>
        ) : history.length === 0 ? (
          <div className="text-center py-10 text-slate-400 text-sm">
            No queries yet — run your first analysis on the Analyst page.
          </div>
        ) : (
          history.map((record, i) => (
            <div
              key={i}
              className="grid grid-cols-[1fr_110px_120px_70px_80px] px-4 py-3 border-b border-slate-100 last:border-0 items-center hover:bg-slate-50 transition-colors"
            >
              <span className="text-sm text-slate-700 truncate pr-4">
                {record.question.length > 60
                  ? `${record.question.slice(0, 60)}…`
                  : record.question}
              </span>
              <span className="text-xs text-indigo-600 truncate">
                {record.symbols.slice(0, 3).join(', ')}
                {record.symbols.length > 3 ? '…' : ''}
              </span>
              <span>
                <span
                  className={`text-xs border rounded px-1.5 py-0.5 ${
                    TYPE_COLORS[record.analysis_type] || TYPE_COLORS.comprehensive
                  }`}
                >
                  {record.analysis_type}
                </span>
              </span>
              <span className="text-xs text-slate-400">
                {record.processing_time?.toFixed(1)}s
              </span>
              <button
                type="button"
                onClick={() => handleReplay(record)}
                className="flex items-center gap-1 text-xs text-indigo-600 hover:text-indigo-800 font-medium transition-colors"
              >
                <ExternalLink size={11} />
                Replay
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
