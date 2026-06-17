import { supabase } from './supabase'
import type { ProjectListParams } from './queryKeys'
import type {
  CreateProjectPayload,
  DashboardStats,
  ProjectDetail,
  ProjectListResponse,
} from '../types/project'
export type UserRole = 'user' | 'admin' | 'portfolio_manager'

export class ApiError extends Error {
  status: number

  constructor(message: string, status: number) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}
const API_BASE = import.meta.env.DEV
  ? '/api/v1'
  : (import.meta.env.VITE_API_URL ?? '/api/v1')

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
  must_change_password: boolean
  email_verified: boolean
}

export type InviteAdminUserPayload = {
  email: string
  role: 'user' | 'admin'
  full_name: string
}

export type InviteAdminUserResponse = {
  user: AdminUser
  email_sent: boolean
  message: string
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

export type AuditLog = {
  id: string
  actor_id: string | null
  actor_email: string | null
  actor_name: string | null
  action: string
  resource: string | null
  details: Record<string, unknown>
  created_at: string
}

export type PaginatedAuditLogs = {
  items: AuditLog[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export type CreateAuditLogPayload = {
  action: string
  resource?: string
  details?: Record<string, unknown>
}

export const AUDIT_PAGE_SIZE = 25

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
    throw new ApiError(message, response.status)
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
    inviteUser: (payload: InviteAdminUserPayload) =>
      request<InviteAdminUserResponse>('/admin/users/invite', {
        method: 'POST',
        body: JSON.stringify(payload),
      }),
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
    listLogs: (page = 1, pageSize = AUDIT_PAGE_SIZE) =>
      request<PaginatedAuditLogs>(
        `/admin/logs?page=${page}&page_size=${pageSize}`,
      ),
    recordLog: (payload: CreateAuditLogPayload) =>
      request<AuditLog>('/admin/logs', {
        method: 'POST',
        body: JSON.stringify(payload),
      }),
  },

  audit: {
    recordEvent: (payload: CreateAuditLogPayload) =>
      request<{ id: string; action: string; created_at: string }>('/audit/events', {
        method: 'POST',
        body: JSON.stringify(payload),
      }),
  },

  dashboard: {
    getStats: () => request<DashboardStats>('/dashboard/stats'),
  },

  projects: {
    list: (params: ProjectListParams = {}) => {
      const query = new URLSearchParams()
      if (params.page) query.set('page', String(params.page))
      if (params.limit) query.set('limit', String(params.limit))
      if (params.status) query.set('status', params.status)
      if (params.search) query.set('search', params.search)
      const suffix = query.toString()
      return request<ProjectListResponse>(`/projects${suffix ? `?${suffix}` : ''}`)
    },
    create: (payload: CreateProjectPayload) =>
      request<ProjectDetail>('/projects', {
        method: 'POST',
        body: JSON.stringify(payload),
      }),
  },
}
