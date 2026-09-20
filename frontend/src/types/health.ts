export interface HealthResponse {
  status: string
  application: string
}

export type ConnectionStatus = 'checking' | 'connected' | 'disconnected'
