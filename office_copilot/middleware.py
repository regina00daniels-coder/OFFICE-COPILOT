from __future__ import annotations

from apps.tenants.models import Tenant
from office_copilot.tenancy import set_current_tenant


class TenantMiddleware:
    """Resolve tenant from request host or X-Tenant header and bind it to request/context."""

    TENANT_HEADER = "HTTP_X_TENANT"
    TENANT_COOKIE = "tenant_hint"

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().split(":")[0].lower()
        tenant_hint = request.META.get(self.TENANT_HEADER, "").strip().lower()
        if not tenant_hint:
            tenant_hint = request.COOKIES.get(self.TENANT_COOKIE, "").strip().lower()

        tenant = None
        if tenant_hint:
            tenant = Tenant.objects.filter(domain=tenant_hint, is_active=True).first()
        if tenant is None:
            tenant = Tenant.objects.filter(domain=host, is_active=True).first()
        if tenant is None and getattr(request, "user", None) is not None and request.user.is_authenticated:
            tenant = Tenant.objects.filter(id=request.user.tenant_id, is_active=True).first()

        request.tenant = tenant
        set_current_tenant(tenant)
        response = self.get_response(request)
        set_current_tenant(None)
        return response
