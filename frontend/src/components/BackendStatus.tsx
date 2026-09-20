import type { ConnectionStatus } from '../types/health'

interface BackendStatusProps {
  status: ConnectionStatus
}

const statusCopy: Record<ConnectionStatus, { label: string; className: string }> = {
  checking: {
    label: 'Checking…',
    className: 'bg-slate-500/20 text-slate-200 ring-slate-500/40',
  },
  connected: {
    label: 'Connected',
    className: 'bg-emerald-500/15 text-emerald-300 ring-emerald-500/40',
  },
  disconnected: {
    label: 'Disconnected',
    className: 'bg-rose-500/15 text-rose-300 ring-rose-500/40',
  },
}

export function BackendStatus({ status }: BackendStatusProps) {
  const { label, className } = statusCopy[status]

  return (
    <div className="mt-10 flex items-center justify-center gap-3 text-sm sm:justify-start sm:text-base">
      <span className="text-slate-400">Backend Status:</span>
      <span
        className={`inline-flex items-center gap-2 rounded-full px-3 py-1 font-medium ring-1 ${className}`}
      >
        <span
          className={`h-2 w-2 rounded-full ${
            status === 'connected'
              ? 'bg-emerald-400'
              : status === 'disconnected'
                ? 'bg-rose-400'
                : 'bg-slate-400'
          }`}
          aria-hidden="true"
        />
        {label}
      </span>
    </div>
  )
}
