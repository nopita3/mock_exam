# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository. Use it as the team map for how the frontend, backend, database, authentication, and logging pieces fit together.

## Project Overview

This is a **Supervisor Tracking System** with a **Vite frontend** and **FastAPI backend**.

- **Frontend**: Modern Vite-based SPA framework (React/Vue/Svelte-ready)
- **Backend**: REST API using FastAPI with SQLModel, located in `../backend/`
- **Communication**: Frontend communicates with backend via HTTP/WebSocket on `http://localhost:8000`

## System Map

The intended development flow is:

1. The frontend collects a Google ID token and sends it to `POST /auth/google`.
2. The backend validates the Google identity, enforces the `@essence.ac.th` domain, and checks whether the user has completed the `/auth/verify` email-link flow.
3. The backend issues the app JWT only after identity, domain, and verification checks pass.
4. Protected frontend calls send the app JWT as `Authorization: Bearer ...`; Google tokens are only for login.
5. Business rules live in services, while routers stay thin and schemas define request and response shapes.
6. API activity is logged through `create_api_log`, with success and token-failure paths covered in the routers.

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

## Team Development Rules

- Authentication is Google OAuth only; do not introduce password-based login.
- Every account must belong to exactly one role: `student`, `teacher`, or `admin`.
- Keep user identity centered on Google email, first name, last name, role, and verification state.
- Enforce the `@essence.ac.th` email domain in backend validation, not only in the UI.
- Treat email verification as part of user activation; unverified users should not be treated as fully active.
- Preserve the JWT-based app session model for protected endpoints.

## Permission Matrix

- Admin can read, update, and delete all user, teacher, and student records.
- Admin cannot create new user, teacher, or student rows directly from the admin workflow; new accounts are created only through the registration flows.
- Admin can read, create, update, and delete score records.
- Teacher can read all student data.
- Teacher can read, create, update, and delete score records.
- Teacher can read only their own teacher record; they do not have access to other teacher records.
- Student can read only their own student record and their own score data.
- Student has no permission to read, create, update, or delete other users’ data.
- For admin and teacher score maintenance, the UI should first ask for `studentID`, pull the current score data, let the user edit the loaded list, and then submit the update or delete action back to the database.
- For admin user maintenance, the UI should follow the same lookup-first pattern before update or delete so the form is populated from the current database row.

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

### Connection Points

- Login and verification: `backend/api/routers/auth.py`, `backend/services/user.py`, `backend/template/verification.html`
- User and role data: `backend/database/models.py`, `backend/api/schemas/users.py`
- Student and teacher workflows: `backend/api/routers/student.py`, `backend/api/routers/teacher.py`, `backend/services/student.py`, `backend/services/teacher.py`
- Admin and audit views: `backend/api/routers/admin.py`, `backend/services/admin.py`, `backend/utils.py`
- UI forms for admin and teacher updates should be lookup-first, not blank-entry-first, when editing records.

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
- **Verification Flow**: `/auth/verify` completes account activation before app JWT access
- **Logging**: `create_api_log` should stay in the request path for auth, student, teacher, and admin actions

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
   - Backend validates Google identity during login and JWT tokens for protected requests
   - Frontend stores JWT and maintains session state

4. **When Changing Features**:
   - Update the router for transport-level validation and response wiring
   - Update the service for business rules and persistence behavior
   - Update the schema if request or response shapes change
   - Update the database migration if the data model changes

## Development Notes

- **HMR**: Vite hot module replacement active during `npm run dev`
- **Backend CORS**: Configured for `localhost:5173` in development
- **API Documentation**: Backend Scalar docs available at `http://localhost:8000/scalar/`
- **Database**: PostgreSQL with async SQLModel ORM
- **Authentication**: Google OAuth login plus app JWT session tokens
- **Verification**: Email-link verification is required before a user is considered active
- **Logs**: API logs are part of normal request handling, not a separate batch job

## Database Models

- `User`: Base user table with role enum and Google identity fields
- `Student`/`Teacher`: Role-specific tables linked via `user_id` foreign key
- `Score`: Exam scores linked to students
- `Log`: API request audit trail

## Change Map

Use this as the starting point when you need to connect a feature request to the code:

- Auth, Google sign-in, verification, domain policy: `backend/api/routers/auth.py`, `backend/services/user.py`, `backend/cores/security.py`
- User lifecycle and role data: `backend/database/models.py`, `backend/api/schemas/users.py`
- Student flows and classroom data: `backend/api/routers/student.py`, `backend/services/student.py`, Alembic migrations
- Teacher flows and score entry: `backend/api/routers/teacher.py`, `backend/services/teacher.py`
- Admin tools and logs: `backend/api/routers/admin.py`, `backend/services/admin.py`, `backend/utils.py`, `backend/middelwares/log_control.py`

## Environment Variables (from .env)

- `POSTGRES_SERVER`, `POSTGRES_PORT`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`
- `REDIS_HOST`, `REDIS_PORT`
- `JWT_SECRET`, `JWT_ALGORITHM`
- `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REDIRECT_URI`
- `ADMIN_CODE`, `TEACHER_CODE`: Registration codes
- Email settings for verification
