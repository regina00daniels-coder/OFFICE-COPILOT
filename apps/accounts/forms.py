from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from apps.tenants.models import Tenant
from .models import User


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Username"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": "Password"}))
    tenant_domain = forms.CharField(required=False, widget=forms.TextInput(attrs={"placeholder": "Tenant domain (optional)"}))


class RegisterForm(UserCreationForm):
    tenant_domain = forms.CharField(help_text="Existing tenant domain (example: a.local)")
    email = forms.EmailField(required=False)

    class Meta:
        model = User
        fields = ("username", "email", "tenant_domain", "password1", "password2")

    def clean_tenant_domain(self):
        domain = self.cleaned_data["tenant_domain"].strip().lower()
        tenant = Tenant.objects.filter(domain=domain, is_active=True).first()
        if not tenant:
            raise forms.ValidationError("Tenant domain not found.")
        self._tenant = tenant
        return domain

    def save(self, commit=True):
        user = super().save(commit=False)
        user.tenant = getattr(self, "_tenant", None)
        user.role = User.Role.USER
        if commit:
            user.save()
        return user
