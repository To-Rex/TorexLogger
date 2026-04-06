import { useEffect, useState } from 'react'
import {
  getProjects,
  createProject,
  deleteProject as deleteProjectApi,
  regenerateKey,
  Project,
} from '../services/api'

export default function Projects() {
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [newProject, setNewProject] = useState({ name: '', description: '' })
  const [submitting, setSubmitting] = useState(false)
  const [showKeyModal, setShowKeyModal] = useState(false)
  const [currentKey, setCurrentKey] = useState('')
  const [copyingId, setCopyingId] = useState<string | null>(null)

  useEffect(() => {
    loadProjects()
  }, [])

  const loadProjects = async () => {
    try {
      const data = await getProjects()
      setProjects(data)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitting(true)
    try {
      await createProject(newProject)
      setShowModal(false)
      setNewProject({ name: '', description: '' })
      loadProjects()
    } catch (err) {
      console.error(err)
    } finally {
      setSubmitting(false)
    }
  }

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this project?')) return
    try {
      await deleteProjectApi(id)
      loadProjects()
    } catch (err) {
      console.error(err)
    }
  }

  const handleRegenerateKey = async (id: string) => {
    try {
      const res = await regenerateKey(id)
      setCurrentKey(res.api_key)
      setShowKeyModal(true)
      loadProjects()
    } catch (err) {
      console.error(err)
    }
  }

  const copyToClipboard = async (key: string, id: string) => {
    try {
      setCopyingId(id)
      await navigator.clipboard.writeText(key)
      setTimeout(() => setCopyingId(null), 2000)
    } catch (err) {
      console.error(err)
      setCopyingId(null)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-text-secondary">Loading...</div>
      </div>
    )
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-semibold text-text-primary">Projects</h1>
          <p className="text-text-secondary text-sm mt-1">Manage your logging projects</p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="px-4 py-2.5 rounded-lg bg-primary text-background font-medium hover:bg-primary-hover transition-all"
        >
          New Project
        </button>
      </div>

      <div className="bg-background-secondary border border-border rounded-xl overflow-hidden">
        {projects.length === 0 ? (
          <div className="p-12 text-center">
            <div className="w-12 h-12 rounded-full bg-surface mx-auto mb-4 flex items-center justify-center">
              <svg className="w-6 h-6 text-text-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
              </svg>
            </div>
            <p className="text-text-secondary text-sm">No projects yet. Create one to get started.</p>
          </div>
        ) : (
          <table className="w-full">
            <thead>
              <tr className="border-b border-border">
                <th className="text-left p-4 text-text-secondary text-xs uppercase tracking-wide font-medium">Name</th>
                <th className="text-left p-4 text-text-secondary text-xs uppercase tracking-wide font-medium">Description</th>
                <th className="text-left p-4 text-text-secondary text-xs uppercase tracking-wide font-medium">API Key</th>
                <th className="text-left p-4 text-text-secondary text-xs uppercase tracking-wide font-medium">Created</th>
                <th className="text-right p-4 text-text-secondary text-xs uppercase tracking-wide font-medium">Actions</th>
              </tr>
            </thead>
            <tbody>
              {projects.map((project) => (
                <tr
                  key={project.id}
                  className="border-b border-border last:border-0 hover:bg-surface/50 transition-colors"
                >
                  <td className="p-4">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
                        <span className="text-primary font-semibold text-sm">{project.name.charAt(0).toUpperCase()}</span>
                      </div>
                      <span className="font-medium text-text-primary">{project.name}</span>
                    </div>
                  </td>
                  <td className="p-4 text-text-secondary">
                    {project.description || '-'}
                  </td>
                  <td className="p-4">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-sm text-text-secondary">
                        {project.api_key
                          ? project.api_key.slice(0, 8) + '...' + project.api_key.slice(-4)
                          : '-'}
                      </span>
                      {project.api_key && (
                        <button
                          onClick={() => copyToClipboard(project.api_key, project.id)}
                          className="p-1.5 rounded hover:bg-surface text-text-muted hover:text-primary transition-colors"
                          title="Copy full key"
                        >
                          {copyingId === project.id ? (
                            <svg className="w-4 h-4 text-success" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                            </svg>
                          ) : (
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                            </svg>
                          )}
                        </button>
                      )}
                    </div>
                  </td>
                  <td className="p-4 text-text-secondary text-sm">
                    {new Date(project.created_at).toLocaleDateString()}
                  </td>
                  <td className="p-4 text-right">
                    <div className="flex items-center justify-end gap-2">
                      <button
                        onClick={() => handleRegenerateKey(project.id)}
                        className="px-3 py-1.5 rounded-lg text-sm text-text-secondary hover:bg-surface hover:text-primary transition-colors"
                      >
                        Regenerate
                      </button>
                      <button
                        onClick={() => handleDelete(project.id)}
                        className="px-3 py-1.5 rounded-lg text-sm text-text-secondary hover:bg-surface hover:text-error transition-colors"
                      >
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="w-full max-w-md p-6 bg-background-secondary border border-border rounded-xl">
            <h2 className="text-xl font-semibold mb-6 text-text-primary">Create Project</h2>
            <form onSubmit={handleCreate}>
              <div className="mb-5">
                <label className="block text-xs font-medium text-text-secondary uppercase tracking-wide mb-2">
                  Project Name
                </label>
                <input
                  type="text"
                  value={newProject.name}
                  onChange={(e) =>
                    setNewProject({ ...newProject, name: e.target.value })
                  }
                  className="w-full px-4 py-3 rounded-lg bg-surface border border-border text-text-primary focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary transition-all"
                  required
                />
              </div>
              <div className="mb-6">
                <label className="block text-xs font-medium text-text-secondary uppercase tracking-wide mb-2">
                  Description (optional)
                </label>
                <textarea
                  value={newProject.description}
                  onChange={(e) =>
                    setNewProject({ ...newProject, description: e.target.value })
                  }
                  className="w-full px-4 py-3 rounded-lg bg-surface border border-border text-text-primary focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary transition-all resize-none h-24"
                />
              </div>
              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="flex-1 px-4 py-2.5 rounded-lg bg-surface text-text-secondary hover:bg-surface-hover hover:text-text-primary transition-all"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="flex-1 px-4 py-2.5 rounded-lg bg-primary text-background font-medium hover:bg-primary-hover transition-all disabled:opacity-50"
                >
                  {submitting ? 'Creating...' : 'Create'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showKeyModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="w-full max-w-md p-6 bg-background-secondary border border-border rounded-xl">
            <h2 className="text-xl font-semibold mb-2 text-text-primary">API Key Generated</h2>
            <p className="text-sm text-text-secondary mb-5">
              Copy your new API key now. You won&apos;t be able to see it again.
            </p>
            <div className="flex gap-2 mb-5">
              <input
                type="text"
                value={currentKey}
                readOnly
                className="flex-1 px-4 py-3 rounded-lg bg-surface border border-border text-text-primary font-mono text-sm"
              />
              <button
                onClick={() => copyToClipboard(currentKey, 'modal')}
                className="px-5 py-3 rounded-lg bg-primary text-background font-medium hover:bg-primary-hover transition-all"
              >
                {copyingId === 'modal' ? 'Copied!' : 'Copy'}
              </button>
            </div>
            <button
              onClick={() => setShowKeyModal(false)}
              className="w-full px-4 py-2.5 rounded-lg bg-surface text-text-secondary hover:bg-surface-hover hover:text-text-primary transition-all"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  )
}