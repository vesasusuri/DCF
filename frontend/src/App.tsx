import { useEffect, useState } from 'react'
import { api } from './lib/api'

type HealthResponse = {
  status: string
  environment: string
}

function App() {
  const [health, setHealth] = useState<HealthResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api
      .getHealth()
      .then(setHealth)
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  return (
    <main>
      <h1>DCF</h1>
      <p>React + Vite frontend connected to a FastAPI backend with Supabase.</p>

      <section className="card">
        <h2>API Health</h2>
        {loading && <span className="status loading">Checking backend...</span>}
        {!loading && health && (
          <span className="status ok">
            {health.status} ({health.environment})
          </span>
        )}
        {!loading && error && <span className="status error">{error}</span>}
        <p style={{ marginTop: '1rem' }}>
          API base URL: <code>{import.meta.env.VITE_API_URL ?? '/api/v1'}</code>
        </p>
      </section>
    </main>
  )
}

export default App
