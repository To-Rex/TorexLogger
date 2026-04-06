import { useEffect, useState, useRef } from 'react'
import { getProjects, connectWebSocket, Project, LogEntry } from '../services/api'

export default function LiveLogs() {
  const [projects, setProjects] = useState<Project[]>([])
  const [selectedProject, setSelectedProject] = useState<string>('')
  const [level, setLevel] = useState<string>('')
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [connected, setConnected] = useState(false)
  const [loading, setLoading] = useState(true)
  const wsRef = useRef<WebSocket | null>(null)
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    loadProjects()
    return () => {
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
  }, [])

  useEffect(() => {
    if (selectedProject) {
      connect()
    }
  }, [selectedProject, level])

  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight
    }
  }, [logs])

  const loadProjects = async () => {
    const data = await getProjects()
    setProjects(data)
    if (data.length > 0) {
      setSelectedProject(data[0].id)
    }
  }

  const connect = () => {
    if (wsRef.current) {
      wsRef.current.close()
    }

    setConnected(false)
    setLoading(true)

    const ws = connectWebSocket(
      selectedProject,
      (data) => {
        setLogs((prev) => [...prev.slice(-99), data])
      },
      (error) => {
        console.error('WebSocket connection error:', error)
        setLoading(false)
      },
      level || undefined
    )

    ws.onopen = () => {
      setConnected(true)
      setLoading(false)
    }
    ws.onclose = () => {
      setConnected(false)
      setLoading(false)
    }
    ws.onerror = (err) => {
      console.error('WebSocket error:', err)
      setConnected(false)
      setLoading(false)
    }

    wsRef.current = ws
  }

  const getLevelColor = (lvl: string) => {
    switch (lvl) {
      case 'error':
        return 'text-error'
      case 'warning':
        return 'text-warning'
      case 'info':
        return 'text-info'
      case 'debug':
        return 'text-text-muted'
      default:
        return 'text-text-secondary'
    }
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-semibold text-text-primary">Live Logs</h1>
          <p className="text-text-secondary text-sm mt-1">Real-time log streaming</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <div
              className={`w-2 h-2 rounded-full ${
                connected ? 'bg-success animate-pulse' : 'bg-error'
              }`}
            />
            <span className="text-sm text-text-secondary">
              {connected ? 'Connected' : 'Disconnected'}
            </span>
          </div>
        </div>
      </div>

      <div className="flex gap-3 mb-5">
        <select
          value={selectedProject}
          onChange={(e) => setSelectedProject(e.target.value)}
          className="px-4 py-2.5 rounded-lg bg-surface border border-border text-text-primary focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary transition-all"
        >
          {projects.map((p) => (
            <option key={p.id} value={p.id}>
              {p.name}
            </option>
          ))}
        </select>

        <select
          value={level}
          onChange={(e) => setLevel(e.target.value)}
          className="px-4 py-2.5 rounded-lg bg-surface border border-border text-text-primary focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary transition-all"
        >
          <option value="">All Levels</option>
          <option value="info">Info</option>
          <option value="warning">Warning</option>
          <option value="error">Error</option>
          <option value="debug">Debug</option>
        </select>

        <button
          onClick={connect}
          className="px-4 py-2.5 rounded-lg bg-primary text-background font-medium hover:bg-primary-hover transition-all"
        >
          Reconnect
        </button>

        <button
          onClick={() => setLogs([])}
          className="px-4 py-2.5 rounded-lg bg-surface border border-border text-text-secondary hover:bg-surface-hover hover:text-text-primary transition-all"
        >
          Clear
        </button>
      </div>

      <div
        ref={containerRef}
        className="bg-background-secondary border border-border rounded-xl overflow-auto max-h-[calc(100vh-250px)]"
      >
        {!connected && loading ? (
          <div className="p-12 text-center text-text-secondary">
            Connecting to WebSocket...
          </div>
        ) : logs.length === 0 ? (
          <div className="p-12 text-center text-text-secondary">
            Waiting for logs...
          </div>
        ) : (
          <table className="w-full">
            <thead className="sticky top-0 bg-background-secondary z-10">
              <tr className="border-b border-border">
                <th className="text-left p-4 text-text-secondary text-xs uppercase tracking-wide font-medium w-48">
                  Timestamp
                </th>
                <th className="text-left p-4 text-text-secondary text-xs uppercase tracking-wide font-medium w-28">
                  Level
                </th>
                <th className="text-left p-4 text-text-secondary text-xs uppercase tracking-wide font-medium w-40">
                  Device
                </th>
                <th className="text-left p-4 text-text-secondary text-xs uppercase tracking-wide font-medium">
                  Message
                </th>
              </tr>
            </thead>
              <tbody>
                {logs.map((log, idx) => (
                  <tr
                    key={log.id || idx}
                    className="border-b border-border last:border-0 hover:bg-surface/30 transition-colors"
                  >
                    <td className="p-4 text-sm text-text-muted font-mono">
                      {new Date(log.timestamp).toLocaleTimeString()}
                    </td>
                    <td className="p-4">
                      <span className={`font-medium ${getLevelColor(log.level)}`}>
                        {log.level}
                      </span>
                    </td>
                    <td className="p-4 text-sm text-text-secondary font-mono">
                      {log.device || '-'}
                    </td>
                    <td className="p-4 font-mono text-sm text-text-primary">{log.message}</td>
                  </tr>
                ))}
              </tbody>
          </table>
        )}
      </div>
    </div>
  )
}