# CLAUDE.md - Full Stack FastAPI Template

## Project Overview

Full-stack web application template with:
- **Backend**: Python FastAPI REST API with SQLModel ORM
- **Frontend**: React/TypeScript SPA with TanStack Router/Query
- **Database**: PostgreSQL
- **Infrastructure**: Docker Compose with Traefik reverse proxy

## Technology Stack

### Backend
- FastAPI (Python 3.10+)
- SQLModel ORM (SQLAlchemy + Pydantic)
- Alembic for migrations
- JWT authentication (HS256)
- Password hashing: Argon2/BCrypt

### Frontend
- React 19 + TypeScript 5
- Vite 7 (build tool)
- TanStack Router (file-based routing)
- TanStack Query (server state)
- React Hook Form + Zod (forms/validation)
- Tailwind CSS 4 + shadcn/ui
- Biome (linter/formatter)

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app entry
│   ├── models.py            # SQLModel ORM models
│   ├── crud.py              # CRUD operations
│   ├── api/
│   │   ├── main.py          # Router setup
│   │   ├── deps.py          # Dependency injection
│   │   └── routes/          # API endpoints (login, users, items)
│   ├── core/
│   │   ├── config.py        # Pydantic Settings
│   │   ├── db.py            # Database setup
│   │   └── security.py      # JWT/password hashing
│   └── alembic/versions/    # Migration scripts
├── tests/                   # Pytest tests
└── pyproject.toml           # Dependencies and tool config

frontend/
├── src/
│   ├── main.tsx             # React entry
│   ├── routes/              # File-based routing
│   ├── components/          # React components
│   │   └── ui/              # shadcn/ui components
│   ├── client/              # Auto-generated API client
│   └── hooks/               # Custom React hooks
├── package.json
├── biome.json               # Linter config
└── playwright.config.ts     # E2E test config
```

## Common Commands

### Backend

```bash
cd backend

# Install dependencies
uv sync

# Run dev server
fastapi dev app/main.py

# Database migrations
alembic revision --autogenerate -m "Description"
alembic upgrade head

# Testing
pytest                       # Run all tests
pytest -x                    # Stop on first failure
pytest --cov=app             # With coverage

# Code quality
uv run ruff check .          # Lint
uv run ruff format .         # Format
uv run mypy app/             # Type check
```

### Frontend

```bash
cd frontend

# Install and run
bun install
bun run dev                  # Dev server at http://localhost:5173

# Build
bun run build                # Production build

# Code quality
bun run lint                 # Biome lint/format

# E2E tests
bunx playwright test
bunx playwright test --ui    # Interactive mode
```

### Docker

```bash
docker compose watch         # Dev stack with hot reload
docker compose up -d         # Start in background
docker compose down -v       # Stop and clean volumes

# Generate API client after backend changes
bash ./scripts/generate-client.sh
```

### Development URLs (Docker)

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- Swagger Docs: http://localhost:8000/docs
- Adminer (DB): http://localhost:8080
- Mailcatcher: http://localhost:1080

## Key Patterns

### Backend

**Model Structure** (app/models.py):
```python
class UserBase(SQLModel):        # Shared fields
class UserCreate(UserBase):      # POST request body
class UserUpdate(UserBase):      # PUT request body
class UserPublic(UserBase):      # API response
class User(UserBase, table=True): # Database table
```

**Dependencies** (app/api/deps.py):
- `SessionDep` - Database session injection
- `CurrentUser` - Extract user from JWT token
- `get_current_active_superuser` - Admin-only routes

**Settings** (app/core/config.py):
- Uses Pydantic Settings with `.env` file
- Access via `settings` singleton

### Frontend

**File-based Routing**: Routes in `src/routes/` auto-generate `routeTree.gen.ts`

**API Client**: Auto-generated from OpenAPI spec in `src/client/`

**Form Pattern**: React Hook Form + Zod schema validation

## Testing

### Backend (pytest)

```bash
bash ./scripts/test.sh           # Run in Docker
bash ./scripts/test-local.sh     # Run locally
```

Key fixtures in `backend/tests/conftest.py`:
- `db` - Database session
- `client` - FastAPI TestClient
- `superuser_token_headers` - Admin auth headers
- `normal_user_token_headers` - User auth headers

### Frontend (Playwright)

```bash
bunx playwright test
```

Requires backend running: `docker compose up -d --wait backend`

## Environment Variables

Key variables in `.env`:

```
DOMAIN=localhost
SECRET_KEY=changethis              # MUST change for production
FIRST_SUPERUSER=admin@example.com
FIRST_SUPERUSER_PASSWORD=changethis
POSTGRES_PASSWORD=changethis
```

Generate secure secret:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Code Style

- **Backend**: Ruff (lint/format), MyPy (types) - config in `pyproject.toml`
- **Frontend**: Biome - config in `biome.json`
- **Pre-commit**: `uv run prek run --all-files`

## Common Tasks

**Add new database model**:
1. Add model to `backend/app/models.py`
2. `alembic revision --autogenerate -m "Add model"`
3. `alembic upgrade head`
4. `bash ./scripts/generate-client.sh`

**Add new API endpoint**:
1. Create route in `backend/app/api/routes/`
2. Include router in `backend/app/api/main.py`
3. Regenerate frontend client if needed
