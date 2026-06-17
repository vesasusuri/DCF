export type ProjectListParams = {
  page?: number
  limit?: number
  status?: string
  search?: string
}

export const queryKeys = {
  dashboard: {
    stats: ['dashboard', 'stats'] as const,
  },
  projects: {
    all: ['projects'] as const,
    list: (params: ProjectListParams) => ['projects', 'list', params] as const,
    detail: (id: string) => ['projects', 'detail', id] as const,
  },
}
