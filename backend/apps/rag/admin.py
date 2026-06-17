from django.contrib import admin

from .models import DocumentChunk

@admin.register(DocumentChunk)
class DocumentChunkAdmin(admin.ModelAdmin):
    list_display = ("id", "document", "created_at")
    search_fields = ("text", "document__filename")
    readonly_fields = ("id", "created_at")
