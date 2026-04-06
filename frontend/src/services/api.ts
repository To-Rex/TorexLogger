import { useAuthStore } from '../stores/authStore'

const API_BASE = '/api'

async function getHeaders() {
  const { token } = useAuthStore.getState()
  return {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${token}`,
  }
}

function handleAuthError() {
  const logout = useAuthStore.getState().logout
  logout()
  window.location.href = '/login'
}

export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
}

export interface Project {
  id: string
  name: string
  description: string | null
  api_key: string
  created_at: string
  updated_at: string
}

export interface LogEntry {
  id: string
  project_id: string
  level: string
  message: string
  timestamp: string
  metadata: Record<string, unknown> | null
  device: string | null
  created_at: string
}

export interface LogListResponse {
  logs: LogEntry[]
  total: number
  limit: number
  offset: number
}

export async function login(data: LoginRequest): Promise<LoginResponse> {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  if (!res.ok) {
    const err = await res.json()
    throw new Error(err.detail || 'Login failed')
  }
  return res.json()
}

export async function getProjects(): Promise<Project[]> {
  const res = await fetch(`${API_BASE}/projects`, {
    headers: await getHeaders(),
  })
  if (res.status === 401) {
    handleAuthError()
    throw new Error('Unauthorized')
  }
  if (!res.ok) {
    throw new Error('Failed to fetch projects')
  }
  return res.json()
}

export async function createProject(data: {
  name: string
  description?: string
}): Promise<Project> {
  const res = await fetch(`${API_BASE}/projects`, {
    method: 'POST',
    headers: await getHeaders(),
    body: JSON.stringify(data),
  })
  if (res.status === 401) {
    handleAuthError()
    throw new Error('Unauthorized')
  }
  if (!res.ok) {
    const err = await res.json()
    throw new Error(err.detail || 'Failed to create project')
  }
  return res.json()
}

export async function deleteProject(id: string): Promise<void> {
  const res = await fetch(`${API_BASE}/projects/${id}`, {
    method: 'DELETE',
    headers: await getHeaders(),
  })
  if (res.status === 401) {
    handleAuthError()
    throw new Error('Unauthorized')
  }
  if (!res.ok) {
    throw new Error('Failed to delete project')
  }
}

export async function regenerateKey(id: string): Promise<{ api_key: string }> {
  const res = await fetch(`${API_BASE}/projects/${id}/regenerate-key`, {
    method: 'POST',
    headers: await getHeaders(),
  })
  if (res.status === 401) {
    handleAuthError()
    throw new Error('Unauthorized')
  }
  if (!res.ok) {
    throw new Error('Failed to regenerate key')
  }
  return res.json()
}

export async function getDevices(projectId: string): Promise<string[]> {
  const params = new URLSearchParams()
  params.set('project_id', projectId)

  const res = await fetch(`${API_BASE}/admin/logs/devices?${params}`, {
    headers: await getHeaders(),
  })
  if (res.status === 401) {
    handleAuthError()
    throw new Error('Unauthorized')
  }
  if (!res.ok) {
    throw new Error('Failed to fetch devices')
  }
  const data = await res.json()
  return data.devices
}

export async function getLogs(
  projectId: string,
  options: {
    level?: string
    startDate?: string
    endDate?: string
    device?: string
    limit?: number
    offset?: number
  } = {}
): Promise<LogListResponse> {
  const params = new URLSearchParams()
  params.set('project_id', projectId)
  if (options.level) params.set('level', options.level)
  if (options.startDate) params.set('start_date', options.startDate)
  if (options.endDate) params.set('end_date', options.endDate)
  if (options.device) params.set('device', options.device)
  if (options.limit) params.set('limit', String(options.limit))
  if (options.offset) params.set('offset', String(options.offset))

  const res = await fetch(`${API_BASE}/admin/logs?${params}`, {
    headers: await getHeaders(),
  })
  if (res.status === 401) {
    handleAuthError()
    throw new Error('Unauthorized')
  }
  if (!res.ok) {
    throw new Error('Failed to fetch logs')
  }
  return res.json()
}

export function connectWebSocket(
  projectId: string,
  onMessage: (data: LogEntry) => void,
  onError?: (error: Event) => void,
  level?: string
) {
  const params = new URLSearchParams()
  params.set('project_id', projectId)
  if (level) params.set('level', level)

  const ws = new WebSocket(`/ws/logs?${params}`)

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      onMessage(data)
    } catch (e) {
      console.error('Failed to parse WebSocket message:', e)
    }
  }

  ws.onerror = (error) => {
    onError?.(error)
  }

  return ws
}

export interface CreateLogRequest {
  level: 'info' | 'warning' | 'error' | 'debug'
  message: string
  timestamp?: string
  meta?: Record<string, unknown>
  device?: string
}

export async function createLog(
  apiKey: string,
  data: CreateLogRequest
): Promise<LogEntry> {
  const res = await fetch(`${API_BASE}/logs`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': apiKey,
    },
    body: JSON.stringify(data),
  })
  if (!res.ok) {
    const err = await res.json()
    throw new Error(err.detail || 'Failed to create log')
  }
  return res.json()
}

export async function createBatchLogs(
  apiKey: string,
  logs: CreateLogRequest[]
): Promise<LogEntry[]> {
  const res = await fetch(`${API_BASE}/logs/batch`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': apiKey,
    },
    body: JSON.stringify({ logs }),
  })
  if (!res.ok) {
    const err = await res.json()
    throw new Error(err.detail || 'Failed to create batch logs')
  }
  return res.json()
}