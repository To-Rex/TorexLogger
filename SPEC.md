# TorexLogger - Centralized Logging System Specification

## Project Overview
- **Project Name**: TorexLogger
- **Type**: Centralized Logging System (Backend + Admin Panel)
- **Core Functionality**: Multi-project log aggregation with real-time streaming and admin management
- **Target Users**: Development teams managing logs from mobile, web, and backend applications

---

## Architecture

### Backend (FastAPI)
```
backend/
├── app/
│   ├── domain/           # Domain entities and interfaces
│   │   ├── entities/
│   │   └── repositories/
│   ├── application/     # Use cases
│   │   └── usecases/
│   ├── infrastructure/  # Database, external services
│   │   ├── database/
│   │   └── redis/
│   ├── presentation/    # API endpoints
│   │   ├── routes/
│   │   └── schemas/
│   └── main.py
├── requirements.txt
├── .env.example
└── Dockerfile
```

### Frontend (React + Vite)
```
frontend/
├── src/
│   ├── components/
│   ├── pages/
│   ├── hooks/
│   ├── services/
│   ├── stores/
│   └── styles/
├── .env.example
├── Dockerfile
└── vite.config.ts
```

---

## Database Schema (PostgreSQL)

### projects
| Column | Type | Constraints |
|--------|------|--------------|
| id | UUID | PRIMARY KEY |
| name | VARCHAR(255) | UNIQUE, NOT NULL |
| description | TEXT | NULLABLE |
| created_at | TIMESTAMP | NOT NULL |
| updated_at | TIMESTAMP | NOT NULL |

### api_keys
| Column | Type | Constraints |
|--------|------|--------------|
| id | UUID | PRIMARY KEY |
| project_id | UUID | FOREIGN KEY -> projects(id) |
| key_hash | VARCHAR(255) | NOT NULL |
| name | VARCHAR(255) | NOT NULL |
| is_active | BOOLEAN | DEFAULT TRUE |
| created_at | TIMESTAMP | NOT NULL |
| expires_at | TIMESTAMP | NULLABLE |

### logs
| Column | Type | Constraints |
|--------|------|--------------|
| id | UUID | PRIMARY KEY |
| project_id | UUID | FOREIGN KEY -> projects(id), INDEX |
| level | VARCHAR(20) | NOT NULL, INDEX |
| message | TEXT | NOT NULL |
| timestamp | TIMESTAMP | NOT NULL, INDEX |
| metadata | JSONB | NULLABLE |
| created_at | TIMESTAMP | NOT NULL |

### admin_users
| Column | Type | Constraints |
|--------|------|--------------|
| id | UUID | PRIMARY KEY |
| username | VARCHAR(255) | UNIQUE, NOT NULL |
| password_hash | VARCHAR(255) | NOT NULL |
| created_at | TIMESTAMP | NOT NULL |

---

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/auth/login | Admin login (JWT) |
| POST | /api/auth/refresh | Refresh JWT token |

### Projects
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/projects | List all projects |
| POST | /api/projects | Create project |
| GET | /api/projects/{id} | Get project details |
| PUT | /api/projects/{id} | Update project |
| DELETE | /api/projects/{id} | Delete project |
| POST | /api/projects/{id}/regenerate-key | Regenerate API key |

### Logs (API Key Auth)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/logs | Create single log |
| POST | /api/logs/batch | Create batch logs |
| GET | /api/logs | Query logs |

### WebSocket
| Endpoint | Description |
|----------|-------------|
| /ws/logs | Real-time log streaming |

---

## UI/UX Specification

### Color Palette
- **Background Dark**: #0f1419
- **Background Light**: #1a2332
- **Surface**: #242d3d
- **Primary**: #3b82f6
- **Success**: #22c55e
- **Warning**: #f59e0b
- **Error**: #ef4444
- **Text Primary**: #f1f5f9
- **Text Secondary**: #94a3b8
- **Border**: #334155

### Typography
- **Font Family**: "Inter", system-ui, sans-serif
- **Headings**: 700 weight
- **Body**: 400 weight
- **Code**: "JetBrains Mono", monospace

### Layout
- **Sidebar**: 240px fixed width
- **Main Content**: Fluid
- **Max Width**: 1400px
- **Spacing**: 8px base unit

### Components
- **Buttons**: Rounded (8px), hover states
- **Cards**: Rounded (12px), subtle shadows
- **Inputs**: Rounded (8px), focus rings
- **Tables**: Striped, sticky headers

---

## Acceptance Criteria

1. Multiple projects can be created with unique API keys
2. Logs are ingested via HTTP with x-api-key header
3. JWT required for admin access
4. WebSocket streams logs in real-time
5. Logs queryable with filters (project, level, date range)
6. Admin panel responsive with dark mode
7. Docker containers for backend and frontend
8. Clean Architecture maintained in backend
9. All endpoints validated and secure
10. Batch log insertion supported