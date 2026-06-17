import { useMutation, useQueryClient } from '@tanstack/react-query'

import { api } from '../lib/api'
import { queryKeys } from '../lib/queryKeys'
import type { CreateProjectPayload } from '../types/project'

export function useCreateProject() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (payload: CreateProjectPayload) => api.projects.create(payload),
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: queryKeys.dashboard.stats }),
        queryClient.invalidateQueries({ queryKey: queryKeys.projects.all }),
      ])
    },
  })
}
