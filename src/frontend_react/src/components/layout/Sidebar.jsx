import { NavLink } from 'react-router-dom'
import { BarChart2, Clock, PieChart } from 'lucide-react'
import { useHealth } from '../../hooks/useHealth'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const NAV = [
  { to: '/', end: true, icon: BarChart2, label: 'Analyst' },
  { to: '/history', end: false, icon: Clock, label: 'History' },
  { to: '/portfolio', end: false, icon: PieChart, label: 'Portfolio' },
]

export function Sidebar() {
  const online = useHealth()

  return (
    <aside className="w-52 bg-slate-900 flex flex-col h-screen fixed left-0 top-0 p-3 z-10">
      <div className="px-2 py-4 border-b border-slate-800 mb-3">
        <div className="text-white font-bold text-sm tracking-tight">MarketSage</div>
        <div className="text-indigo-400 text-xs mt-0.5">AI Analytics</div>
      </div>

      <nav className="flex flex-col gap-1 flex-1">
        {NAV.map(({ to, end, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) =>
              `flex items-center gap-2.5 px-3 py-2 rounded-md text-sm transition-colors ${
                isActive
                  ? 'bg-indigo-500/20 border border-indigo-500/30 text-white font-medium'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800'
              }`
            }
          >
            <Icon size={15} />
            {label}
          </NavLink>
        ))}
      </nav>

      <div
        className={`p-2.5 rounded-md text-xs border ${
          online
            ? 'bg-emerald-950/50 border-emerald-800 text-emerald-400'
            : 'bg-red-950/50 border-red-800 text-red-400'
        }`}
      >
        <div className="font-medium">{online ? '● Backend online' : '● Backend offline'}</div>
        <div className="text-slate-500 mt-0.5 truncate">{API_BASE}</div>
      </div>
    </aside>
  )
}
