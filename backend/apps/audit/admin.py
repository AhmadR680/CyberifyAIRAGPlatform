from django.contrib import admin

from .models import AuditLog

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("action", "user", "workspace", "resource_type", "created_at")
    list_filter = ("action", "resource_type", "workspace")
    search_fields = ("action", "resource_type", "resource_id", "user__email")
    readonly_fields = ("id", "created_at")
