import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ReferenceLine, ResponsiveContainer,
} from 'recharts'
import { computeRSI } from '../../utils/chartUtils'

export function TechnicalChart({ data }) {
  if (!data || Object.keys(data).length === 0) return null
  const firstSymbol = Object.keys(data)[0]
  const rows = data[firstSymbol]
  if (!rows || rows.length === 0) return null

  const closes = rows.map((r) => r.close)
  const rsiValues = computeRSI(closes)
  const chartData = rows
    .map((r, i) => ({
      date: r.date,
      rsi: rsiValues[i] !== null ? parseFloat(Number(rsiValues[i]).toFixed(1)) : null,
    }))
    .filter((r) => r.rsi !== null)

  return (
    <div className="flex flex-col h-full gap-1">
      <div className="text-xs font-medium text-slate-500">
        {firstSymbol} — RSI (14-period)
      </div>
      <div className="flex-1">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
            <XAxis
              dataKey="date"
              tick={{ fontSize: 10 }}
              tickFormatter={(v) => v.slice(5)}
              interval="preserveStartEnd"
            />
            <YAxis domain={[0, 100]} tick={{ fontSize: 10 }} width={32} />
            <Tooltip
              formatter={(v) => [Number(v).toFixed(1), 'RSI']}
              labelStyle={{ fontSize: 11 }}
              contentStyle={{ fontSize: 11 }}
            />
            <ReferenceLine y={70} stroke="#ef4444" strokeDasharray="4 2"
              label={{ value: 'OB 70', fontSize: 9, fill: '#ef4444', position: 'right' }} />
            <ReferenceLine y={30} stroke="#10b981" strokeDasharray="4 2"
              label={{ value: 'OS 30', fontSize: 9, fill: '#10b981', position: 'right' }} />
            <Line type="monotone" dataKey="rsi" stroke="#6366f1" dot={false} strokeWidth={1.5} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
