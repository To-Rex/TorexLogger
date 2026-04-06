import { useEffect, useState } from 'react'
import { getProjects, createLog, createBatchLogs, Project } from '../services/api'

export default function TestLog() {
  const [projects, setProjects] = useState<Project[]>([])
  const [selectedProject, setSelectedProject] = useState<string>('')
  const [apiKey, setApiKey] = useState<string>('')
  const [level, setLevel] = useState<'info' | 'warning' | 'error' | 'debug'>('info')
  const [message, setMessage] = useState<string>('')
  const [device, setDevice] = useState<string>('')
  const [metadata, setMetadata] = useState<string>('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<string>('')
  const [error, setError] = useState<string>('')

  useEffect(() => {
    loadProjects()
  }, [])

  useEffect(() => {
    const project = projects.find(p => p.id === selectedProject)
    if (project) {
      setApiKey(project.api_key)
    }
  }, [selectedProject, projects])

  const loadProjects = async () => {
    const data = await getProjects()
    setProjects(data)
    if (data.length > 0) {
      setSelectedProject(data[0].id)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setResult('')
    setError('')

    try {
      let meta: Record<string, unknown> | undefined
      if (metadata.trim()) {
        try {
          meta = JSON.parse(metadata)
        } catch {
          setError('Invalid JSON in metadata')
          setLoading(false)
          return
        }
      }

      const log = await createLog(apiKey, {
        level,
        message,
        device: device || undefined,
        meta,
      })

      setResult(JSON.stringify(log, null, 2))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create log')
    } finally {
      setLoading(false)
    }
  }

  const handleBatchSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setResult('')
    setError('')

    try {
      let meta: Record<string, unknown> | undefined
      if (metadata.trim()) {
        try {
          meta = JSON.parse(metadata)
        } catch {
          setError('Invalid JSON in metadata')
          setLoading(false)
          return
        }
      }

      const logs = await createBatchLogs(apiKey, [
        {
          level,
          message,
          device: device || undefined,
          meta,
        },
      ])

      setResult(JSON.stringify(logs, null, 2))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create batch logs')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-text-primary">Test Log</h1>
        <p className="text-text-secondary text-sm mt-1">Create test logs to verify your logging setup</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-background-secondary border border-border rounded-xl p-6">
          <h2 className="text-lg font-medium text-text-primary mb-4">Configuration</h2>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm text-text-secondary mb-2">Project</label>
              <select
                value={selectedProject}
                onChange={(e) => setSelectedProject(e.target.value)}
                className="w-full px-4 py-2.5 rounded-lg bg-surface border border-border text-text-primary focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary transition-all"
              >
                {projects.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm text-text-secondary mb-2">API Key</label>
              <input
                type="text"
                value={apiKey}
                readOnly
                className="w-full px-4 py-2.5 rounded-lg bg-surface border border-border text-text-muted font-mono text-sm"
              />
            </div>
          </div>

          <h2 className="text-lg font-medium text-text-primary mb-4 mt-8">Log Details</h2>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm text-text-secondary mb-2">Level</label>
              <select
                value={level}
                onChange={(e) => setLevel(e.target.value as typeof level)}
                className="w-full px-4 py-2.5 rounded-lg bg-surface border border-border text-text-primary focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary transition-all"
              >
                <option value="debug">Debug</option>
                <option value="info">Info</option>
                <option value="warning">Warning</option>
                <option value="error">Error</option>
              </select>
            </div>

            <div>
              <label className="block text-sm text-text-secondary mb-2">Message</label>
              <textarea
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                rows={3}
                required
                className="w-full px-4 py-2.5 rounded-lg bg-surface border border-border text-text-primary focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary transition-all font-mono text-sm"
                placeholder="Enter log message..."
              />
            </div>

            <div>
              <label className="block text-sm text-text-secondary mb-2">Device (optional)</label>
              <input
                type="text"
                value={device}
                onChange={(e) => setDevice(e.target.value)}
                className="w-full px-4 py-2.5 rounded-lg bg-surface border border-border text-text-primary focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary transition-all"
                placeholder="e.g., iphone-15-pro"
              />
            </div>

            <div>
              <label className="block text-sm text-text-secondary mb-2">Metadata (optional, JSON)</label>
              <textarea
                value={metadata}
                onChange={(e) => setMetadata(e.target.value)}
                rows={3}
                className="w-full px-4 py-2.5 rounded-lg bg-surface border border-border text-text-primary focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary transition-all font-mono text-sm"
                placeholder='{"user_id": "123"}'
              />
            </div>

            <div className="flex gap-3">
              <button
                type="submit"
                disabled={loading || !message}
                className="px-6 py-2.5 rounded-lg bg-primary text-background font-medium hover:bg-primary-hover transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Sending...' : 'Send Single Log'}
              </button>
              
              <button
                type="button"
                onClick={handleBatchSubmit}
                disabled={loading || !message}
                className="px-6 py-2.5 rounded-lg bg-surface border border-border text-text-primary hover:bg-surface-hover transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Sending...' : 'Send Batch Log'}
              </button>
            </div>
          </form>

          {error && (
            <div className="mt-4 p-4 rounded-lg bg-error/10 border border-error/20 text-error text-sm">
              {error}
            </div>
          )}
        </div>

        <div className="bg-background-secondary border border-border rounded-xl p-6">
          <h2 className="text-lg font-medium text-text-primary mb-4">Result</h2>
          
          {result ? (
            <pre className="text-sm text-text-muted font-mono bg-surface p-4 rounded-lg overflow-auto max-h-[500px]">
              {result}
            </pre>
          ) : (
            <div className="text-text-secondary text-sm">
              Log response will appear here...
            </div>
          )}
        </div>
      </div>

      <div className="mt-8 bg-background-secondary border border-border rounded-xl p-6">
        <h2 className="text-lg font-medium text-text-primary mb-4">cURL Example</h2>
        <pre className="text-sm text-text-muted font-mono bg-surface p-4 rounded-lg overflow-auto">
{`curl -X POST http://localhost:8080/api/logs \\
  -H "Content-Type: application/json" \\
  -H "x-api-key: ${apiKey || 'YOUR_API_KEY'}" \\
  -d '{
    "level": "${level}",
    "message": "${message || 'Your message here'}",
    "device": "${device || 'optional-device-id'}",
    "meta": ${metadata || '{}'}
  }'`}
        </pre>
      </div>
    </div>
  )
}