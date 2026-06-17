import { useQuery } from '@tanstack/react-query'

import { api } from '../lib/api'
import { queryKeys, type ProjectListParams } from '../lib/queryKeys'

export function useProjects(params: ProjectListParams, enabled = true) {
  return useQuery({
    queryKey: queryKeys.projects.list(params),
    queryFn: () => api.projects.list(params),
    enabled,
    staleTime: 30_000,
    placeholderData: (previousData) => previousData,
  })
}
