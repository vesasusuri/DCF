import { useParams } from 'react-router-dom'

export function useProject() {
  const { projectId } = useParams()
  return { projectId: projectId ?? null }
}
