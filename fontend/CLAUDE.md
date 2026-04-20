# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Supervisor Tracking System** with a **Vite (latest) frontend** and **FastAPI backend**. 

- **Frontend**: Modern Vite-based SPA framework (React/Vue/Svelte-ready)
- **Backend**: RESTful API using FastAPI with SQLModel, located in `../backend/`
- **Communication**: Frontend communicates with backend via HTTP/WebSocket on `http://localhost:8000`

### Workspace Structure
```
mock_exam/
├── fontend/                    # Frontend: Vite project (THIS FOLDER)
│   ├── src/                    # Source code
│   ├── public/                 # Static assets
│   ├── vite.config.js          # Vite configuration
│   ├── package.json            # Dependencies & scripts
│   └── CLAUDE.md               # This file
└── backend/                    # Backend: FastAPI (parent directory)
    ├── api/, cores/, database/ # Core modules
    ├── config.py, main.py      # Configuration & entry
    └── requirements.txt        # Python dependencies
```

## Frontend Commands (Vite)

```bash
# Install dependencies
npm install

# Development server (HMR enabled)
npm run dev

# Production build
npm run build

# Preview production build locally
npm run preview

# Lint code
npm run lint
```

## Backend Commands (FastAPI)

```bash
# Run backend server (must be running for frontend API calls)
cd ../
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
pytest

# Lint
ruff check .
black .
```

## Architecture

```
mock_exam/
├── backend/
│   ├── api/
│   │   ├── router.py          # Master router aggregating all endpoints
│   │   ├── routers/           # Endpoint modules: auth, admin, teacher, student
│   │   └── schemas/           # Pydantic schemas for request/response validation
│   ├── cores/
│   │   ├── exception.py       # Custom exceptions & global exception handlers
│   │   └── security.py        # JWT token verification, admin/teacher code checks
│   ├── database/
│   │   ├── models.py          # SQLModel tables: User, Student, Teacher, Score, Log
│   │   └── sessions.py        # Async engine & get_session dependency
│   ├── services/              # Business logic layer
│   │   ├── user.py            # Google OAuth, email verification, user CRUD
│   │   ├── admin.py           # Admin operations, log retrieval
│   │   ├── teacher.py         # Score upload, student management
│   │   └── email.py           # Email sending via fastapi-mail
│   ├── middelwares/           # Request logging middleware
│   ├── config.py              # Pydantic settings (DB, JWT, OAuth, Email)
│   ├── utils.py               # JWT encode/decode, email token, API log helper
│   └── main.py                # App init, CORS, lifespan, Scalar docs
└── google-id-token-test.html  # Google OAuth testing page
```

## Frontend-Backend Integration

### API Communication
- **Base URL**: `http://localhost:8000` (dev) or configured prod URL
- **Authentication**: JWT tokens stored in localStorage/cookies
- **Request Headers**: Include `Authorization: Bearer <JWT_TOKEN>` for protected endpoints
- **CORS**: Backend allows frontend domain (configured in FastAPI main.py)

### Key API Endpoints
- `POST /auth/google` - Google OAuth login
- `POST /auth/register` - User registration (teacher/student with verification codes)
- `GET /users/me` - Get current user profile
- `POST /students/` - Create/manage students (teacher/admin)
- `POST /scores/` - Upload exam scores (teacher)
- `GET /logs/` - Retrieve API logs (admin)

### Vite Environment Setup
Create a `.env.local` file in `fontend/` for frontend configuration:
```
VITE_API_BASE_URL=http://localhost:8000
VITE_GOOGLE_CLIENT_ID=<your-google-client-id>
```

Access in frontend code:
```javascript
const apiBaseURL = import.meta.env.VITE_API_BASE_URL;
```

## Key Patterns

- **Dependency Injection**: `get_session` for DB, `verify_token` for auth
- **Service Layer**: Each service extends `BaseService` with generic CRUD
- **Exception Handling**: Custom exceptions (`EntityNotFound`, `ClientNotAuthorized`, etc.) with centralized handlers
- **Email Domain Restriction**: All user emails must end with `@essence.ac.th`
- **Google OAuth**: Login via `POST /auth/google` with Google ID token

## Getting Started (Development)

1. **Backend Setup** (run first):
   ```bash
   cd ../ && pip install -r backend/requirements.txt
   uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Frontend Setup**:
   ```bash
   cd fontend && npm install
   npm run dev
   ```
   Frontend runs on `http://localhost:5173` (Vite default)

3. **Communication Flow**:
   - Frontend calls backend API endpoints
   - Backend validates JWT tokens and returns responses
   - Frontend stores JWT and maintains session state

## Development Notes

- **HMR**: Vite hot module replacement active during `npm run dev`
- **Backend CORS**: Configured for `localhost:5173` in development
- **API Documentation**: Backend Scalar docs available at `http://localhost:8000/scalar/`
- **Database**: PostgreSQL with async SQLModel ORM
- **Authentication**: JWT-based with Google OAuth option

## Database Models

- `User`: Base user table with role enum (teacher/admin/student)
- `Student`/`Teacher`: Role-specific tables linked via `user_id` foreign key
- `Score`: Exam scores linked to students
- `Log`: API request audit trail

## Environment Variables (from .env)

- `POSTGRES_SERVER`, `POSTGRES_PORT`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`
- `REDIS_HOST`, `REDIS_PORT`
- `JWT_SECRET`, `JWT_ALGORITHM`
- `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REDIRECT_URI`
- `ADMIN_CODE`, `TEACHER_CODE`: Registration codes
- Email settings for verification
