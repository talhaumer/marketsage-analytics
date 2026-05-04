import { useState, useEffect } from 'react'
import client from '../api/client'

export function useChartData(symbols, timeframe) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const key = (symbols || []).join(',')

  useEffect(() => {
    if (!symbols || symbols.length === 0) {
      setData(null)
      return
    }
    setLoading(true)
    setError(null)
    client
      .get('/chart-data', { params: { symbols: key, timeframe } })
      .then(({ data: d }) => {
        setData(d)
        setLoading(false)
      })
      .catch((err) => {
        setError(err.message)
        setLoading(false)
      })
  }, [key, timeframe])

  return { data, loading, error }
}
