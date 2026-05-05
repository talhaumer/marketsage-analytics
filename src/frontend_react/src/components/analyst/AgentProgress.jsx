import { useEffect, useState } from 'react'
import { CheckCircle2, Circle, Loader2 } from 'lucide-react'

// Timing matches realistic LangGraph execution order:
// market_research → financial_data → parallel group → final_synthesis
const AGENTS = [
  { key: 'market_research',    label: 'Market Research',    delay: 0,    duration: 1500 },
  { key: 'financial_data',     label: 'Financial Data',     delay: 1500, duration: 2000 },
  { key: 'technical_analysis', label: 'Technical Analysis', delay: 3500, duration: 1800 },
  { key: 'risk_assessment',    label: 'Risk Assessment',    delay: 3700, duration: 2000 },
  { key: 'sentiment_analysis', label: 'Sentiment',          delay: 3900, duration: 1600 },
  { key: 'portfolio_analysis', label: 'Portfolio',          delay: 4100, duration: 1700 },
  { key: 'sector_analysis',    label: 'Sector Analysis',    delay: 4300, duration: 1500 },
  { key: 'crypto_analysis',    label: 'Crypto',             delay: 4500, duration: 1500 },
  { key: 'final_synthesis',    label: 'Final Synthesis',    delay: 6000, duration: 1500 },
]

const INIT_STATES = () => AGENTS.reduce((acc, a) => ({ ...acc, [a.key]: 'pending' }), {})
const INIT_ELAPSED = () => AGENTS.reduce((acc, a) => ({ ...acc, [a.key]: null }), {})

export function AgentProgress({ status }) {
  const [agentStates, setAgentStates] = useState(INIT_STATES)
  const [elapsed, setElapsed] = useState(INIT_ELAPSED)

  useEffect(() => {
    if (status === 'idle') {
      setAgentStates(INIT_STATES())
      setElapsed(INIT_ELAPSED())
      return
    }
    if (status === 'done' || status === 'error') {
      setAgentStates(AGENTS.reduce((acc, a) => ({ ...acc, [a.key]: 'done' }), {}))
      return
    }
    if (status !== 'loading') return

    const startTime = Date.now()
    const timers = []

    AGENTS.forEach((agent) => {
      timers.push(
        setTimeout(() => {
          setAgentStates((prev) => ({ ...prev, [agent.key]: 'running' }))
        }, agent.delay),
      )
      timers.push(
        setTimeout(() => {
          const sec = ((Date.now() - startTime) / 1000).toFixed(1)
          setAgentStates((prev) => ({ ...prev, [agent.key]: 'done' }))
          setElapsed((prev) => ({ ...prev, [agent.key]: sec }))
        }, agent.delay + agent.duration),
      )
    })

    return () => timers.forEach(clearTimeout)
  }, [status])

  const doneCount = Object.values(agentStates).filter((s) => s === 'done').length
  const pct = Math.round((doneCount / AGENTS.length) * 100)

  return (
    <div>
      <div className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">
        Agent Pipeline
      </div>
      <div className="grid grid-cols-2 gap-1 mb-3">
        {AGENTS.map((agent) => {
          const s = agentStates[agent.key]
          return (
            <div
              key={agent.key}
              className={`flex items-center gap-2 px-2 py-1.5 rounded text-xs ${
                s === 'running' ? 'bg-amber-50' : ''
              }`}
            >
              {s === 'done' ? (
                <CheckCircle2 size={13} className="text-emerald-500 shrink-0" />
              ) : s === 'running' ? (
                <Loader2 size={13} className="text-amber-500 animate-spin shrink-0" />
              ) : (
                <Circle size={13} className="text-slate-300 shrink-0" />
              )}
              <span className={s === 'pending' ? 'text-slate-400' : 'text-slate-700 font-medium'}>
                {agent.label}
              </span>
              {elapsed[agent.key] && (
                <span className="ml-auto text-slate-400">{elapsed[agent.key]}s</span>
              )}
            </div>
          )
        })}
      </div>
      <div className="h-1.5 bg-slate-100 rounded-full overflow-hidden">
        <div
          className="h-full bg-gradient-to-r from-indigo-500 to-indigo-400 rounded-full transition-all duration-500"
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  )
}
