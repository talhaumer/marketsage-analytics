import { useState } from 'react'
import { X } from 'lucide-react'

export function SymbolInput({ symbols, onChange, maxSymbols = 20 }) {
  const [input, setInput] = useState('')

  const addSymbol = (raw) => {
    const sym = raw.trim().toUpperCase().replace(/[^A-Z0-9.]/g, '')
    if (sym && !symbols.includes(sym) && symbols.length < maxSymbols) {
      onChange([...symbols, sym])
    }
    setInput('')
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault()
      addSymbol(input)
    } else if (e.key === 'Backspace' && !input && symbols.length > 0) {
      onChange(symbols.slice(0, -1))
    }
  }

  return (
    <div className="flex flex-wrap gap-1.5 p-2 border border-slate-200 rounded-md bg-white min-h-[40px] cursor-text focus-within:ring-2 focus-within:ring-indigo-500 focus-within:border-transparent transition-shadow">
      {symbols.map((sym) => (
        <span
          key={sym}
          className="flex items-center gap-1 bg-indigo-50 text-indigo-700 border border-indigo-200 rounded px-2 py-0.5 text-xs font-medium"
        >
          {sym}
          <button
            type="button"
            onClick={() => onChange(symbols.filter((s) => s !== sym))}
            className="hover:text-indigo-900 transition-colors"
            aria-label={`Remove ${sym}`}
          >
            <X size={10} />
          </button>
        </span>
      ))}
      {symbols.length < maxSymbols && (
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          onBlur={() => input.trim() && addSymbol(input)}
          placeholder={symbols.length === 0 ? 'AAPL, MSFT… (Enter to add)' : ''}
          className="flex-1 min-w-[100px] outline-none text-xs bg-transparent placeholder-slate-400 text-slate-700"
        />
      )}
    </div>
  )
}
