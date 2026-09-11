# HRMS Production Deployment (Vercel + Neon PostgreSQL)

## Architecture

- Single Vercel project using **Services**: frontend (Vite + React + Bootstrap) and backend (Django REST API + SimpleJWT) share one domain.
- Database: Neon PostgreSQL via `DATABASE_URL` (pooled connection, `sslmode=require`).
- Storage: Cloudinary for uploaded media.
- Static files: WhiteNoise compressed manifest storage, collected automatically by Vercel.

## Repository layout

- `vercel.json` (repo root): defines the two services and top-level routing.
- `frontend/`: Vite + React app.
- `backend/`: Django project. `api/index.py` exposes the WSGI app; `manage.py` is detected by Vercel.

Routing owned by the root `vercel.json`:

```
/api/*      -> backend service
/admin/*    -> backend service
/static/*   -> backend service
/*          -> frontend service (SPA)
```

The backend service receives the original path (`/api/...` stays `/api/...`), so Django URL patterns under `api/v1/...` work unchanged.

## Deploy

1. Import this repository into Vercel (root directory = repo root).
2. Add the backend environment variables below to the project (shared by both services).
3. Add `VITE_API_BASE_URL=/api` for the frontend build.
4. Deploy. Both services build in one project.

## Backend environment variables

```env
DEBUG=False
SECRET_KEY=replace-with-a-secure-random-key
DATABASE_URL=postgresql://username:password@host/database?sslmode=require
ALLOWED_HOSTS=your-app.vercel.app
CORS_ALLOWED_ORIGINS=https://your-app.vercel.app
CSRF_TRUSTED_ORIGINS=https://your-app.vercel.app
FRONTEND_URL=https://your-app.vercel.app
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
```

- `ALLOWED_HOSTS` must list the exact deployed hostname (and any custom domain) without a scheme.
- `CORS_ALLOWED_ORIGINS` / `CSRF_TRUSTED_ORIGINS` must contain the full frontend origin.
- Remaining variables are read by `backend/config/settings.py`; local development falls back to PostgreSQL when `DATABASE_URL` is not set.

## Frontend environment variable

```env
VITE_API_BASE_URL=/api
```

`frontend/src/api/client.js` turns it into `/api/v1` — no `/api/api/` duplication.

Local dev: leave it unset (client falls back to `http://127.0.0.1:8000/api`) or use `vercel dev` at the repo root to run both services together.

## Database setup (run once, manually, against the Neon URL)

```bash
cd backend
.venv\Scripts\python.exe manage.py migrate
.venv\Scripts\python.exe manage.py createsuperuser
```

Migrations must be applied manually before use; Vercel does not run them on deployment. `conn_max_age=0` keeps serverless connections short, and the pooled Neon URL is required.

## Verify after deploy

- `GET https://your-app.vercel.app/api/health/` returns `{"status": "ok", "service": "hrms-backend"}`
- Login, JWT refresh, payroll, and Cloudinary uploads work.
- Unknown `ALLOWED_HOSTS`/origins are rejected.

## Troubleshooting

- `DisallowedHost` / 500 on first load: fix `ALLOWED_HOSTS` and redeploy.
- CORS/CSRF errors: confirm origins match the frontend domain exactly.
- Neon SSL errors: ensure `DATABASE_URL` includes `?sslmode=require` and use the pooled URL.
- Missing static files: WhiteNoise serves them; ensure `collectstatic` output (staticfiles/) is build-generated, not committed.