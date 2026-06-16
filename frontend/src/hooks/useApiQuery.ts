import { useQuery } from '@tanstack/react-query'

import { api } from '../lib/api'

export function useApiQuery() {
  return useQuery({
    queryKey: ['health'],
    queryFn: () => api.getHealth(),
  })
}
