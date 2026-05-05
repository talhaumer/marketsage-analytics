import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts'

const COLORS = ['#6366f1', '#818cf8', '#a5b4fc', '#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']

export function AllocationChart({ symbols, weights }) {
  if (!symbols || symbols.length === 0) return null
  const total = weights.reduce((s, w) => s + Number(w), 0) || 1
  const chartData = symbols.map((sym, i) => ({
    name: sym,
    value: parseFloat(((Number(weights[i]) / total) * 100).toFixed(1)),
  }))

  return (
    <ResponsiveContainer width="100%" height="100%">
      <PieChart>
        <Pie
          data={chartData}
          cx="50%"
          cy="50%"
          innerRadius="38%"
          outerRadius="65%"
          dataKey="value"
          nameKey="name"
        >
          {chartData.map((_, i) => (
            <Cell key={i} fill={COLORS[i % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip formatter={(v) => [`${v}%`]} contentStyle={{ fontSize: 11 }} />
        <Legend wrapperStyle={{ fontSize: 11 }} />
      </PieChart>
    </ResponsiveContainer>
  )
}
