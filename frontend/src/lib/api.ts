import { supabase } from './supabase'

const API_BASE = import.meta.env.VITE_API_URL ?? '/api/v1'

export type HealthResponse = {
  status: string
  environment: string
}

export type AdminStats = {
  users_total: number
  admins_total: number
  users_active_24h: number
  environment: string
  api_status: string
}

export type AdminUser = {
  id: string
  email: string
  full_name: string
  role: 'user' | 'admin'
  created_at: string | null
  last_sign_in_at: string | null
}

export type CreateAdminUserPayload = {
  email: string
  password: string
  role: 'user' | 'admin'
  full_name: string
}

export type UpdateAdminUserPayload = {
  role?: 'user' | 'admin'
  full_name?: string
  password?: string
}

async function getAuthHeaders(): Promise<HeadersInit> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  }

  if (supabase) {
    const { data } = await supabase.auth.getSession()
    const token = data.session?.access_token
    if (token) {
      headers.Authorization = `Bearer ${token}`
    }
  }

  return headers
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      ...(await getAuthHeaders()),
      ...init?.headers,
    },
  })

  if (!response.ok) {
    let message = `Request failed with status ${response.status}`
    try {
      const body = (await response.json()) as { detail?: string }
      if (body.detail) message = body.detail
    } catch {
      const text = await response.text()
      if (text) message = text
    }
    throw new Error(message)
  }

  if (response.status === 204) {
    return undefined as T
  }

  return response.json() as Promise<T>
}

export const api = {
  getHealth: () => request<HealthResponse>('/health'),

  admin: {
    getStats: () => request<AdminStats>('/admin/stats'),
    listUsers: () => request<AdminUser[]>('/admin/users'),
    createUser: (payload: CreateAdminUserPayload) =>
      request<AdminUser>('/admin/users', {
        method: 'POST',
        body: JSON.stringify(payload),
      }),
    updateUser: (userId: string, payload: UpdateAdminUserPayload) =>
      request<AdminUser>(`/admin/users/${userId}`, {
        method: 'PATCH',
        body: JSON.stringify(payload),
      }),
  },
}
