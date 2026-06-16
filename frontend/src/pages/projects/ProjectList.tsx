import { Link } from 'react-router-dom'

import { Card } from '../../components/ui/Card'
import { PlaceholderPage } from '../../layouts/AppLayout'
import { SCREEN_IDS } from '../../lib/constants'

export function ProjectList() {
  return (
    <div className="space-y-4">
      <PlaceholderPage title={SCREEN_IDS.S01} description="Project dashboard placeholder." />
      <Card title="Quick links">
        <Link to="/projects/demo/upload" className="text-sm text-blue-600 hover:underline">
          Open demo project upload
        </Link>
      </Card>
    </div>
  )
}
