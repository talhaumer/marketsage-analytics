import { useState, useEffect } from 'react'
import client from '../api/client'

export function useHealth() {
  const [online, setOnline] = useState(false)

  useEffect(() => {
    const check = () =>
      client
        .get('/health')
        .then(() => setOnline(true))
        .catch(() => setOnline(false))
    check()
    const id = setInterval(check, 30000)
    return () => clearInterval(id)
  }, [])

  return online
}
