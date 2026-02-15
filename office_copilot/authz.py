from django.core.exceptions import PermissionDenied


def enforce_tenant_access(request):
    if not request.user.is_authenticated:
        raise PermissionDenied("Authentication required")
    if request.tenant is None:
        raise PermissionDenied("Tenant is required")
    if request.user.is_superuser:
        return
    if request.user.tenant_id != request.tenant.id:
        raise PermissionDenied("Cross-tenant access denied")


def enforce_role(request, allowed_roles):
    enforce_tenant_access(request)
    if request.user.is_superuser:
        return
    if request.user.role not in allowed_roles:
        raise PermissionDenied("Role not allowed")
