import { useState } from 'react'
import { AlertCircle } from 'lucide-react'
import { QueryPanel } from '../components/analyst/QueryPanel'
import { AnalysisResult } from '../components/analyst/AnalysisResult'
import { AgentProgress } from '../components/analyst/AgentProgress'
import { ChartPanel } from '../components/charts/ChartPanel'
import { useAnalysis } from '../hooks/useAnalysis'
import { useChartData } from '../hooks/useChartData'

export function Analyst() {
  const { status, result, error, run } = useAnalysis()
  const [symbols, setSymbols] = useState([])
  const [timeframe, setTimeframe] = useState('1y')
  const { data: chartData, loading: chartLoading, error: chartError } = useChartData(
    symbols,
    timeframe,
  )

  const handleRun = (payload) => {
    run(payload)
  }

  return (
    <div className="flex flex-col h-full">
      {/* Top bar */}
      <div className="bg-white border-b border-slate-200 px-5 py-3 flex items-center justify-between flex-shrink-0">
        <div>
          <h1 className="text-sm font-bold text-slate-900">AI Market Analyst</h1>
          <p className="text-xs text-slate-400 mt-0.5">Powered by 8 specialized agents</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="bg-emerald-50 text-emerald-700 border border-emerald-200 px-2 py-0.5 rounded-full text-xs font-medium">
            Groq LLM
          </span>
          <span className="bg-blue-50 text-blue-700 border border-blue-200 px-2 py-0.5 rounded-full text-xs font-medium">
            LangGraph
          </span>
        </div>
      </div>

      {/* Split body */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left panel: query form + result */}
        <div className="w-[420px] flex-shrink-0 border-r border-slate-200 flex flex-col bg-white overflow-y-auto">
          <QueryPanel
            onRun={handleRun}
            loading={status === 'loading'}
            onSymbolsChange={setSymbols}
            onTimeframeChange={setTimeframe}
          />

          {status === 'error' && (
            <div className="mx-4 mt-3 flex items-start gap-2 bg-red-50 border border-red-200 text-red-700 rounded-md p-3 text-xs">
              <AlertCircle size={13} className="shrink-0 mt-0.5" />
              <span>{error || 'Backend unreachable — make sure python main.py is running.'}</span>
            </div>
          )}

          {status === 'done' && result && (
            <div className="p-4 flex-1">
              <div className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-3">
                AI Analysis
              </div>
              <AnalysisResult result={result} />
            </div>
          )}
        </div>

        {/* Right panel: agent progress + charts */}
        <div className="flex-1 flex flex-col overflow-hidden bg-slate-50">
          <div className="bg-white border-b border-slate-200 p-4 flex-shrink-0">
            <AgentProgress status={status} />
          </div>
          <div className="flex-1 p-4 overflow-hidden flex flex-col min-h-0">
            <ChartPanel
              chartData={chartData}
              loading={chartLoading}
              error={chartError}
            />
          </div>
        </div>
      </div>
    </div>
  )
}
