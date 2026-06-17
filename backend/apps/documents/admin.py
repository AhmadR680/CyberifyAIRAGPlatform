from django.contrib import admin
from .models import Document

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("filename", "workspace", "uploaded_by", "status", "content_type", "created_at")
    list_filter = ("status", "workspace", "content_type")
    search_fields = ("filename", "extracted_text")
    readonly_fields = ("id", "created_at", "updated_at")