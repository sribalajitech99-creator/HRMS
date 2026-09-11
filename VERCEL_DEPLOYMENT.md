# Vercel Production Deployment Guide

## Final architecture

- Frontend: Vite + React + Bootstrap, hosted as a separate Vercel project at `https://portal.YOURDOMAIN.com`
- Backend: Django REST API, hosted as a separate Vercel Python project at `https://api-portal.YOURDOMAIN.com`
- Database: Neon PostgreSQL via `DATABASE_URL`
- Storage: Cloudinary for uploaded media
- Local development: still supports MySQL fallback via `.env` files

## Files changed

- [backend/config/settings.py](backend/config/settings.py)
- [backend/config/urls.py](backend/config/urls.py)
- [backend/requirements.txt](backend/requirements.txt)
- [backend/api/index.py](backend/api/index.py)
- [backend/vercel.json](backend/vercel.json)
- [backend/.env.example](backend/.env.example)
- [frontend/src/api/client.js](frontend/src/api/client.js)
- [frontend/.env.example](frontend/.env.example)
- [frontend/vercel.json](frontend/vercel.json)
- [.gitignore](.gitignore)

## Vercel frontend setup

1. Import the GitHub repo in Vercel.
2. Set project name to `hrms-frontend`.
3. Root directory: `frontend`.
4. Framework preset: Vite.
5. Install command: `npm install`.
6. Build command: `npm run build`.
7. Output directory: `dist`.
8. Add environment variable:
   - `VITE_API_BASE_URL=https://api-portal.YOURDOMAIN.com/api`
9. Add custom domain: `portal.YOURDOMAIN.com`.

## Vercel backend setup

1. Import the same GitHub repo again.
2. Set project name to `hrms-backend`.
3. Root directory: `backend`.
4. Framework preset: Other.
5. Use the Python serverless project with `backend/vercel.json` and `backend/api/index.py`.
6. Add environment variables from the checklist below.
7. Add custom domain: `api-portal.YOURDOMAIN.com`.

## Neon setup

1. Create a new empty PostgreSQL database in Neon.
2. Copy the pooled connection string.
3. Set `DATABASE_URL` to the pooled URL with `?sslmode=require` if required by your deployment.
4. Keep local MySQL development enabled via fallback config when `DATABASE_URL` is not defined.

## Cloudinary setup

1. Create a Cloudinary account.
2. Copy cloud name, API key, and API secret.
3. Add them to the backend environment.
4. Use the default storage backend configured in Django so existing image fields continue to work without model changes.

## Environment variable checklist

### Backend

```env
DJANGO_SECRET_KEY=REPLACE_WITH_SECURE_RANDOM_VALUE
DJANGO_DEBUG=False
DATABASE_URL=REPLACE_WITH_NEON_POOLED_DATABASE_URL
DJANGO_ALLOWED_HOSTS=api-portal.YOURDOMAIN.com,YOUR-BACKEND.vercel.app
CORS_ALLOWED_ORIGINS=https://portal.YOURDOMAIN.com,https://YOUR-FRONTEND.vercel.app
CSRF_TRUSTED_ORIGINS=https://portal.YOURDOMAIN.com,https://YOUR-FRONTEND.vercel.app
FRONTEND_URL=https://portal.YOURDOMAIN.com
CLOUDINARY_CLOUD_NAME=REPLACE_ME
CLOUDINARY_API_KEY=REPLACE_ME
CLOUDINARY_API_SECRET=REPLACE_ME
```

### Frontend

```env
VITE_API_BASE_URL=https://api-portal.YOURDOMAIN.com/api
```

## Domain setup order

1. Deploy the temporary Vercel backend URL.
2. Test `/api/health/`.
3. Add `api-portal.YOURDOMAIN.com` to the backend project.
4. Add DNS record as Vercel prompts.
5. Confirm HTTPS.
6. Update backend allowed hosts.
7. Deploy frontend.
8. Add `portal.YOURDOMAIN.com` to the frontend project.
9. Add DNS record as Vercel prompts.
10. Update CORS and CSRF trusted origins.
11. Set the frontend API URL.
12. Redeploy both projects.
13. Verify with a private/incognito browser and a mobile device.

## Initial schema migration commands

Run these manually in a safe environment before production usage:

```bash
cd backend
python manage.py check
python manage.py showmigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py check --deploy
```

## Superuser creation

```bash
cd backend
python manage.py createsuperuser
```

## Deployment order

1. Push the repository to GitHub.
2. Import both projects into Vercel.
3. Configure backend env variables.
4. Deploy backend and verify health endpoint.
5. Configure frontend env variable and custom domain.
6. Deploy frontend and verify app loads.
7. Run manual migrations against the Neon database from a safe shell.

## Testing checklist

- `/api/health/` returns status `ok`
- Django admin route remains accessible
- Frontend app loads on custom domain
- `/login` route redirects correctly
- JWT login and refresh still work
- API calls use `https://api-portal.YOURDOMAIN.com/api`
- Cloudinary uploads succeed
- Static files resolve without server crashes
- Unknown origins are rejected

## Rollback procedure

1. Keep current production Vercel projects intact.
2. Revert Git commit causing the issue.
3. Redeploy the previous Vercel build.
4. Restore environment variables if they were changed.
5. Keep MySQL unchanged as rollback data source until PostgreSQL validation succeeds.

## MySQL-to-PostgreSQL migration plan

1. Back up MySQL safely.
2. Record table counts.
3. Create a clean Neon Postgres database.
4. Apply Django schema migrations.
5. Export application data safely.
6. Exclude framework-generated records if required.
7. Import into PostgreSQL.
8. Reset sequences.
9. Validate employees, companies, attendance, leave, salaries, payslips and assets.
10. Compare row counts.
11. Test login and permissions.
12. Leave MySQL as the rollback source.

Possible issues:
- MySQL zero dates
- Boolean conversion differences
- Character encoding mismatches
- Time-zone conversion drift
- Duplicate unique values
- Foreign-key ordering issues
- Auto-increment to sequence differences
- File paths to local media directories
- Content types and permissions mismatches
- Password hash format changes
- Decimal salary rounding differences

## Known Vercel serverless limitations

- Long-running payroll generation may exceed function limits
- Large Excel imports should be moved to worker processing outside the request
- Background jobs and file operations should use external workers
- Local filesystem writes are not persistent inside Vercel
- WebSockets and scheduled tasks need a different platform or managed queue worker
- Very large PDFs and zip generation may hit runtime or memory limits

## Troubleshooting

### 404 on React routes

- Confirm that the frontend project has `frontend/vercel.json` and a SPA rewrite rule.
- Check `dist` is set as the output directory.

### Django `DisallowedHost`

- Ensure `DJANGO_ALLOWED_HOSTS` includes the deployed backend domain and `.vercel.app`.

### CORS errors

- Confirm `CORS_ALLOWED_ORIGINS` contains the exact frontend domain and Vercel domain.

### CSRF errors

- Add the frontend domain to `CSRF_TRUSTED_ORIGINS`.

### 500 server errors

- Check backend logs in Vercel.
- Validate environment variables and DB connectivity.

### Neon SSL errors

- Confirm the database URL includes `sslmode=require` when needed.
- Use the Neon pooled connection string.

### Too many PostgreSQL connections

- Use pooled Neon URLs and avoid long-lived DB connections.
- Use serverless-safe behavior with `conn_max_age=0`.

### Missing static files

- Ensure WhiteNoise is installed and the static storage backend is configured.

### Cloudinary upload failures

- Validate `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, and `CLOUDINARY_API_SECRET`.
- Ensure upload size and type validation are handled on the backend.

### Vercel function timeout

- Split large tasks into background jobs or external processing.

### Incorrect `/api/api/` URLs

- Frontend should use `https://api-portal.YOURDOMAIN.com/api` and then append `/v1` only once in the central API client.

### Migration tables missing

- Run `python manage.py migrate` against the Neon database manually before using production endpoints.

### Login works locally but fails in production

- Check `CORS_ALLOWED_ORIGINS`, `CSRF_TRUSTED_ORIGINS`, `DJANGO_ALLOWED_HOSTS`, and the frontend API URL.
- Confirm the deployed backend domain is new and not still pointing at an old host.
