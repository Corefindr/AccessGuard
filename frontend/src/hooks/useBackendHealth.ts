import { useEffect, useState } from 'react'

import { fetchHealth } from '../api/health'
import type { ConnectionStatus } from '../types/health'

const POLL_INTERVAL_MS = 10000

export function useBackendHealth(): ConnectionStatus {
  const [status, setStatus] = useState<ConnectionStatus>('checking')

  useEffect(() => {
    let cancelled = false

    async function checkHealth() {
      try {
        const data = await fetchHealth()
        if (cancelled) {
          return
        }
        setStatus(
          data.status === 'ok' && data.application === 'AccessGuard'
            ? 'connected'
            : 'disconnected',
        )
      } catch {
        if (!cancelled) {
          setStatus('disconnected')
        }
      }
    }

    void checkHealth()
    const intervalId = window.setInterval(() => {
      void checkHealth()
    }, POLL_INTERVAL_MS)

    return () => {
      cancelled = true
      window.clearInterval(intervalId)
    }
  }, [])

  return status
}
