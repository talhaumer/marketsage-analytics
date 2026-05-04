import { useState, useCallback } from 'react'
import client from '../api/client'

export function useAnalysis() {
  const [status, setStatus] = useState('idle')
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const run = useCallback(async (payload) => {
    setStatus('loading')
    setResult(null)
    setError(null)
    try {
      const { data } = await client.post('/analyze', payload)
      if (data.success) {
        setResult(data)
        setStatus('done')
      } else {
        setError(data.error || 'Analysis failed')
        setStatus('error')
      }
    } catch (err) {
      const msg =
        err.response?.data?.detail ||
        err.message ||
        'Backend unreachable — make sure python main.py is running.'
      setError(msg)
      setStatus('error')
    }
  }, [])

  const reset = useCallback(() => {
    setStatus('idle')
    setResult(null)
    setError(null)
  }, [])

  return { status, result, error, run, reset }
}
