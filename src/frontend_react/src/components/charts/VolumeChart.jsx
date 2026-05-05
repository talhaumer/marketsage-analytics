import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
} from 'recharts'
import { mergeByDate } from '../../utils/chartUtils'

const COLORS = ['#6366f1', '#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']

function fmtVol(v) {
  if (v >= 1e9) return `${(v / 1e9).toFixed(1)}B`
  if (v >= 1e6) return `${(v / 1e6).toFixed(1)}M`
  if (v >= 1e3) return `${(v / 1e3).toFixed(1)}K`
  return String(v)
}

export function VolumeChart({ data }) {
  if (!data || Object.keys(data).length === 0) return null
  const symbols = Object.keys(data)
  const merged = mergeByDate(data, 'volume')

  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart data={merged} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
        <XAxis
          dataKey="date"
          tick={{ fontSize: 10 }}
          tickFormatter={(v) => v.slice(5)}
          interval="preserveStartEnd"
        />
        <YAxis tick={{ fontSize: 10 }} width={45} tickFormatter={fmtVol} />
        <Tooltip formatter={(v) => [fmtVol(Number(v))]} labelStyle={{ fontSize: 11 }} contentStyle={{ fontSize: 11 }} />
        <Legend wrapperStyle={{ fontSize: 11 }} />
        {symbols.map((sym, i) => (
          <Bar key={sym} dataKey={sym} fill={COLORS[i % COLORS.length]} opacity={0.8} />
        ))}
      </BarChart>
    </ResponsiveContainer>
  )
}
