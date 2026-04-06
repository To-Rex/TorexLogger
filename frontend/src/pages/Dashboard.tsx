import { useEffect, useState } from 'react'
import { getProjects, Project } from '../services/api'
import { Link } from 'react-router-dom'

export default function Dashboard() {
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)

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

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-text-secondary">Loading...</div>
      </div>
    )
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-text-primary">Dashboard</h1>
        <p className="text-text-secondary text-sm mt-1">Overview of your logging system</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div className="p-5 bg-background-secondary border border-border rounded-xl">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-text-secondary text-xs uppercase tracking-wide">Total Projects</div>
              <div className="text-3xl font-semibold mt-1 text-text-primary">{projects.length}</div>
            </div>
            <div className="w-10 h-10 rounded-lg bg-surface flex items-center justify-center">
              <svg className="w-5 h-5 text-text-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
              </svg>
            </div>
          </div>
        </div>
        
        <div className="p-5 bg-background-secondary border border-border rounded-xl">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-text-secondary text-xs uppercase tracking-wide">Active Keys</div>
              <div className="text-3xl font-semibold mt-1 text-success">
                {projects.filter((p) => p.api_key).length}
              </div>
            </div>
            <div className="w-10 h-10 rounded-lg bg-surface flex items-center justify-center">
              <svg className="w-5 h-5 text-success" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
              </svg>
            </div>
          </div>
        </div>
        
        <div className="p-5 bg-background-secondary border border-border rounded-xl">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-text-secondary text-xs uppercase tracking-wide">System Status</div>
              <div className="text-3xl font-semibold mt-1 text-primary">Healthy</div>
            </div>
            <div className="w-10 h-10 rounded-lg bg-surface flex items-center justify-center">
              <svg className="w-5 h-5 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      <div className="p-6 bg-background-secondary border border-border rounded-xl">
        <div className="flex items-center justify-between mb-5">
          <h2 className="text-lg font-semibold text-text-primary">Recent Projects</h2>
          <Link to="/projects" className="text-sm text-primary hover:text-primary-hover transition-colors">
            View all →
          </Link>
        </div>
        
        {projects.length === 0 ? (
          <p className="text-text-secondary text-sm">No projects yet. Create one to get started.</p>
        ) : (
          <div className="space-y-2">
            {projects.slice(0, 5).map((project) => (
              <div
                key={project.id}
                className="flex items-center justify-between p-4 rounded-lg bg-surface hover:bg-surface-hover transition-colors"
              >
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
                    <span className="text-primary font-semibold text-sm">{project.name.charAt(0).toUpperCase()}</span>
                  </div>
                  <div>
                    <div className="font-medium text-text-primary">{project.name}</div>
                    <div className="text-sm text-text-secondary">
                      {project.description || 'No description'}
                    </div>
                  </div>
                </div>
                <div className="text-sm text-text-muted">
                  {new Date(project.created_at).toLocaleDateString()}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}