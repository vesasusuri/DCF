export type ProjectStatus = 'draft' | 'test' | 'ready' | 'active' | 'archived'

export type LatestRun = {
  runNumber: number | null
  status: string | null
  completedAt: string | null
  createdAt: string | null
}

export type ProjectSummary = {
  id: string
  projectName: string
  clientName: string | null
  assetCount: number
  status: ProjectStatus
  latestRun: LatestRun | null
  assignedTeam: string | null
  createdAt: string | null
  updatedAt: string | null
}

export type ProjectListResponse = {
  items: ProjectSummary[]
  total: number
  page: number
  pages: number
}

export type ProjectDetail = {
  id: string
  projectName: string
  clientName: string | null
  currency: string
  valuationDate: string | null
  reportingLanguage: string
  status: ProjectStatus
  assignedTeam: string | null
  createdBy: string | null
  createdAt: string | null
  updatedAt: string | null
  metadata: Record<string, unknown>
}

export type DashboardStats = {
  openProjects: number
  assetsWithinScope: number
  awaitingReview: number
  reportsPerMonth: number
}

export type CreateProjectPayload = {
  client: string
  projectName: string
  currency: string
  valuationDate: string
  reportingLanguage: string
}
