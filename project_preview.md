# OFFICE-COPILOT Production Preview

## Architecture Overview
- Shared-database, row-level tenant isolation via `Tenant` FK on tenant-owned models.
- Tenant resolution middleware reads `X-Tenant` header first, then request host domain (or domain value via `X-Tenant`).
- `request.tenant` is attached to every request and used by all tenant-aware views.
- Custom `accounts.User` model includes `tenant` FK and `role` field for RBAC.
- Modular apps:
  - `tenants`: tenant lifecycle and identity
  - `accounts`: authentication + user roles
  - `dashboard`: tenant-scoped summary
  - `tasks`, `meetings`, `reporting`, `presentations`: business domains

## Tenant Resolution Flow
1. Incoming request reaches `TenantMiddleware`.
2. Middleware extracts tenant domain from `X-Tenant` header, fallback to host/domain lookup.
3. Active tenant is attached as `request.tenant`.
4. Authorization helpers ensure user belongs to same tenant (except superuser).
5. Views query with `Model.objects.filter(tenant=request.tenant)`.

## Security/Isolation Rules
- Every business model includes a required `tenant` FK.
- Every API view enforces tenant access before read/write.
- Cross-tenant access raises `PermissionDenied`.
- Role gating (`admin`, `staff`, `user`) controls privileged actions such as report creation.

## UI & API Endpoints
- `GET /dashboard/`
- `GET /api/dashboard/summary/`
- `GET /api/dashboard/activity/`
- `GET|POST /api/tasks/`
- `GET|POST /api/meetings/`
- `GET|POST /api/reporting/`
- `POST /api/presentations/ai/text-to-presentation/`

## Migration & Verification Commands
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py test
python manage.py createsuperuser
```

## Deployment Notes
- Configure env vars in production (`DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, DB vars).
- Use `gunicorn` + reverse proxy (`nginx`) and run `collectstatic`.
- Use `WhiteNoise` for static serving in app tier.
- Media should be offloaded to persistent storage (S3 or mounted volume).
