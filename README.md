# TorexLogger - Centralized Logging System

A production-ready centralized logging system with FastAPI backend and React admin panel.

## Features

- **Multi-Project Support**: Create and manage multiple independent projects
- **API Key Authentication**: Secure API key-based log ingestion
- **JWT Admin Authentication**: Secure admin panel access
- **Real-Time Logs**: WebSocket-based live log streaming
- **Log Query API**: Filter logs by project, level, date range with pagination
- **Modern Admin Panel**: React-based dashboard with dark mode

## Quick Start

### Using Docker (Recommended)

```bash
# Start all services
docker-compose up -d

# Access the admin panel
http://localhost:3000

# Default admin credentials
username: admin
password: admin123
```

### Manual Setup

#### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Run the server
python -m uvicorn app.main:app --reload
```

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Run the dev server
npm run dev
```

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/auth/login | Admin login |

### Projects
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/projects | List projects |
| POST | /api/projects | Create project |
| GET | /api/projects/{id} | Get project |
| DELETE | /api/projects/{id} | Delete project |
| POST | /api/projects/{id}/regenerate-key | Regenerate API key |

### Logs (API Key Auth)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/logs | Create log |
| POST | /api/logs/batch | Create batch logs |

### Admin Logs
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/admin/logs | Query logs |

### WebSocket
| Endpoint | Description |
|----------|-------------|
| /ws/logs | Real-time log streaming |

## Environment Variables

### Backend
| Variable | Description | Default |
|----------|-------------|---------|
| DATABASE_URL | PostgreSQL connection string | postgresql+asyncpg://postgres:postgres@localhost:5432/torexlogger |
| JWT_SECRET_KEY | JWT secret key | your-secret-key-change-in-production |
| REDIS_URL | Redis connection string | redis://localhost:6379/0 |
| ADMIN_USERNAME | Admin username | admin |
| ADMIN_PASSWORD | Admin password | admin123 |

## Tech Stack

### Backend
- FastAPI
- SQLAlchemy (async)
- PostgreSQL
- Redis
- JWT (python-jose)
- Passlib

### Frontend
- React 18
- Vite
- TailwindCSS
- Zustand (state management)
- React Router

## Project Structure

```
torexlogger/
├── backend/
│   ├── app/
│   │   ├── domain/          # Entities & interfaces
│   │   ├── application/    # Use cases
│   │   ├── infrastructure/# Database, Redis
│   │   └── presentation/   # API routes
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── stores/
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## Usage

### Sending Logs

```bash
# Single log
curl -X POST http://localhost:8000/api/logs \
  -H "Content-Type: application/json" \
  -H "x-api-key: YOUR_API_KEY" \
  -d '{"level": "info", "message": "User logged in", "timestamp": "2024-01-01T00:00:00Z"}'

# Batch logs
curl -X POST http://localhost:8000/api/logs/batch \
  -H "Content-Type: application/json" \
  -H "x-api-key: YOUR_API_KEY" \
  -d '{"logs": [{"level": "info", "message": "Log 1"}, {"level": "error", "message": "Log 2"}]}'
```

### WebSocket Connection

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/logs?project_id=YOUR_PROJECT_ID');

ws.onmessage = (event) => {
  const log = JSON.parse(event.data);
  console.log(log);
};
```