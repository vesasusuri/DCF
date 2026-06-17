import { useQuery } from '@tanstack/react-query'

import { api } from '../lib/api'
import { queryKeys } from '../lib/queryKeys'

export function useDashboardStats(enabled = true) {
  return useQuery({
    queryKey: queryKeys.dashboard.stats,
    queryFn: () => api.dashboard.getStats(),
    enabled,
    staleTime: 30_000,
  })
}
