import { useEffect, useState } from 'react'
import {
  getProjects,
  getLogs as getLogsApi,
  getDevices,
  Project,
  LogEntry,
} from '../services/api'

export default function Logs() {
  const [projects, setProjects] = useState<Project[]>([])
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [selectedProject, setSelectedProject] = useState<string>('')
  const [level, setLevel] = useState<string>('')
  const [device, setDevice] = useState<string>('')
  const [devices, setDevices] = useState<string[]>([])
  const [loading, setLoading] = useState(false)
  const [total, setTotal] = useState(0)
  const [offset, setOffset] = useState(0)
  const limit = 50

  useEffect(() => {
    loadProjects()
  }, [])

  useEffect(() => {
    if (selectedProject) {
      loadLogs()
    }
  }, [selectedProject, level, device, offset])

  useEffect(() => {
    if (selectedProject) {
      loadDevices()
    }
  }, [selectedProject])

  const loadProjects = async () => {
    const data = await getProjects()
    setProjects(data)
    if (data.length > 0) {
      setSelectedProject(data[0].id)
    }
  }

  const loadDevices = async () => {
    try {
      const deviceList = await getDevices(selectedProject)
      setDevices(deviceList)
    } catch (err) {
      console.error('Failed to load devices:', err)
      setDevices([])
    }
  }

  const loadLogs = async () => {
    setLoading(true)
    try {
      const res = await getLogsApi(selectedProject, {
        level: level || undefined,
        device: device || undefined,
        limit,
        offset,
      })
      setLogs(res.logs)
      setTotal(res.total)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const getLevelColor = (lvl: string) => {
    switch (lvl) {
      case 'error':
        return 'text-error bg-error/10 border-error/20'
      case 'warning':
        return 'text-warning bg-warning/10 border-warning/20'
      case 'info':
        return 'text-info bg-info/10 border-info/20'
      case 'debug':
        return 'text-text-muted bg-surface border-border'
      default:
        return 'text-text-secondary'
    }
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-text-primary">Logs</h1>
        <p className="text-text-secondary text-sm mt-1">View and search through your logs</p>
      </div>

      <div className="flex gap-3 mb-6">
        <select
          value={selectedProject}
          onChange={(e) => {
            setSelectedProject(e.target.value)
            setOffset(0)
          }}
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
          onChange={(e) => {
            setLevel(e.target.value)
            setOffset(0)
          }}
          className="px-4 py-2.5 rounded-lg bg-surface border border-border text-text-primary focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary transition-all"
        >
          <option value="">All Levels</option>
          <option value="info">Info</option>
          <option value="warning">Warning</option>
          <option value="error">Error</option>
          <option value="debug">Debug</option>
        </select>

        <select
          value={device}
          onChange={(e) => {
            setDevice(e.target.value)
            setOffset(0)
          }}
          className="px-4 py-2.5 rounded-lg bg-surface border border-border text-text-primary focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary transition-all"
        >
          <option value="">All Devices</option>
          {devices.map((d) => (
            <option key={d} value={d}>
              {d}
            </option>
          ))}
        </select>
      </div>

      <div className="bg-background-secondary border border-border rounded-xl overflow-hidden">
        <div className="max-h-[calc(100vh-300px)] overflow-auto">
          {loading ? (
            <div className="p-12 text-center text-text-secondary">Loading...</div>
          ) : logs.length === 0 ? (
            <div className="p-12 text-center text-text-secondary">
              No logs found. Select a project and try again.
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
                {logs.map((log) => (
                  <tr key={log.id} className="border-b border-border last:border-0 hover:bg-surface/30 transition-colors">
                    <td className="p-4 text-sm text-text-muted font-mono">
                      {new Date(log.timestamp).toLocaleString()}
                    </td>
                    <td className="p-4">
                      <span
                        className={`inline-flex px-2.5 py-1 rounded-md text-xs font-medium border ${getLevelColor(
                          log.level
                        )}`}
                      >
                        {log.level}
                      </span>
                    </td>
                    <td className="p-4 text-sm text-text-secondary font-mono">
                      {log.device || '-'}
                    </td>
                    <td className="p-4">
                      <div className="font-mono text-sm text-text-primary">{log.message}</div>
                      {log.metadata && (
                        <pre className="text-xs text-text-muted mt-2 font-mono bg-surface p-2 rounded">
                          {JSON.stringify(log.metadata, null, 2)}
                        </pre>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {total > limit && (
        <div className="flex items-center justify-between mt-5">
          <div className="text-text-secondary text-sm">
            Showing {offset + 1}-{Math.min(offset + limit, total)} of {total} logs
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setOffset(Math.max(0, offset - limit))}
              disabled={offset === 0}
              className="px-4 py-2 rounded-lg bg-surface border border-border text-text-secondary hover:bg-surface-hover hover:text-text-primary transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>
            <button
              onClick={() => setOffset(offset + limit)}
              disabled={offset + limit >= total}
              className="px-4 py-2 rounded-lg bg-surface border border-border text-text-secondary hover:bg-surface-hover hover:text-text-primary transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  )
}