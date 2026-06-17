from django.contrib import admin

from .models import WorkflowTask

@admin.register(WorkflowTask)
class WorkflowTaskAdmin(admin.ModelAdmin):
    list_display = ("title", "document", "status", "assignee", "deadline", "created_at")
    list_filter = ("status", "document")
    search_fields = ("title", "description", "assignee")
    readonly_fields = ("id", "created_at", "updated_at")
