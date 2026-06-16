import { Link, Outlet, useParams } from 'react-router-dom'

export function ProjectLayout() {
  const { projectId } = useParams()

  return (
    <div>
      <nav className="mb-4 flex flex-wrap gap-3 text-sm text-slate-600">
        <Link to={`/projects/${projectId}/upload`} className="hover:text-blue-600">
          Upload
        </Link>
        <Link to={`/projects/${projectId}/assumptions`} className="hover:text-blue-600">
          Assumptions
        </Link>
        <Link to={`/projects/${projectId}/runs`} className="hover:text-blue-600">
          Runs
        </Link>
        <Link to={`/projects/${projectId}/reports`} className="hover:text-blue-600">
          Reports
        </Link>
      </nav>
      <Outlet />
    </div>
  )
}
