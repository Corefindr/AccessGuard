import { BackendStatus } from '../components/BackendStatus'
import { useBackendHealth } from '../hooks/useBackendHealth'

export function LandingPage() {
  const status = useBackendHealth()

  return (
    <main className="flex min-h-svh flex-col">
      <header className="border-b border-slate-800/80 px-6 py-4">
        <div className="mx-auto flex w-full max-w-5xl items-center justify-between">
          <p className="text-sm font-semibold tracking-wide text-sky-300">
            AccessGuard
          </p>
          <p className="text-xs uppercase tracking-[0.18em] text-slate-500">
            Phase 1 · Foundation
          </p>
        </div>
      </header>

      <section className="mx-auto flex w-full max-w-5xl flex-1 flex-col justify-center px-6 py-16">
        <p className="text-xs font-semibold uppercase tracking-[0.22em] text-sky-400">
          Service Desk · IT Operations
        </p>
        <h1 className="mt-4 text-4xl font-semibold tracking-tight text-white sm:text-5xl">
          AccessGuard
        </h1>
        <p className="mt-3 max-w-xl text-lg text-slate-300 sm:text-xl">
          IT Access Compliance &amp; Dormancy Management
        </p>
        <p className="mt-6 max-w-2xl text-sm leading-6 text-slate-400 sm:text-base">
          Track employee access across applications, surface dormant or expiring
          entitlements, and prepare for reminders, escalations, and compliance
          reporting. This landing page confirms the frontend can reach the API.
        </p>
        <BackendStatus status={status} />
      </section>
    </main>
  )
}
