/**
 * Merges per-symbol OHLCV arrays into a flat array keyed by date.
 * Used by PriceChart and VolumeChart.
 * @param {Object} chartData - { SYMBOL: [{date, close, volume, ...}] }
 * @param {string} field - 'close' | 'volume'
 */
export function mergeByDate(chartData, field) {
  const dateMap = {}
  Object.entries(chartData).forEach(([sym, rows]) => {
    rows.forEach((row) => {
      if (!dateMap[row.date]) dateMap[row.date] = { date: row.date }
      dateMap[row.date][sym] = row[field]
    })
  })
  return Object.values(dateMap).sort((a, b) => a.date.localeCompare(b.date))
}

/**
 * Computes 14-period RSI from an array of close prices.
 * Returns an array of the same length; the first 14 entries are null.
 */
export function computeRSI(closes, period = 14) {
  if (closes.length < period + 1) return closes.map(() => null)

  const rsi = new Array(period).fill(null)
  let gains = 0
  let losses = 0

  for (let i = 1; i <= period; i++) {
    const d = closes[i] - closes[i - 1]
    if (d > 0) gains += d
    else losses -= d
  }

  let avgGain = gains / period
  let avgLoss = losses / period
  rsi.push(avgLoss === 0 ? 100 : avgGain === 0 ? 0 : 100 - 100 / (1 + avgGain / avgLoss))

  for (let i = period + 1; i < closes.length; i++) {
    const d = closes[i] - closes[i - 1]
    avgGain = (avgGain * (period - 1) + Math.max(d, 0)) / period
    avgLoss = (avgLoss * (period - 1) + Math.max(-d, 0)) / period
    rsi.push(avgLoss === 0 ? 100 : avgGain === 0 ? 0 : 100 - 100 / (1 + avgGain / avgLoss))
  }

  return rsi
}

/**
 * Computes the period % return: (last_close - first_close) / first_close * 100.
 */
export function computeReturn(rows) {
  if (!rows || rows.length < 2) return 0
  const first = rows[0].close
  const last = rows[rows.length - 1].close
  return parseFloat((((last - first) / first) * 100).toFixed(2))
}
