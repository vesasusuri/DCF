const API_BASE = import.meta.env.VITE_API_URL ?? '/api/v1'

type HealthResponse = {
  status: string
  environment: string
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...init?.headers,
    },
    ...init,
  })

  if (!response.ok) {
    const message = await response.text()
    throw new Error(message || `Request failed with status ${response.status}`)
  }

  return response.json() as Promise<T>
}

export const api = {
  getHealth: () => request<HealthResponse>('/health'),
}
