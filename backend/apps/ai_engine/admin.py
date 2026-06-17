from django.contrib import admin

from .models import ContractAnalysis, ComplianceScore, ChatHistory

@admin.register(ContractAnalysis)
class ContractAnalysisAdmin(admin.ModelAdmin):
    list_display = ("id", "document", "created_at")
    search_fields = ("summary", "document__filename")
    readonly_fields = ("id", "created_at")

@admin.register(ComplianceScore)
class ComplianceScoreAdmin(admin.ModelAdmin):
    list_display = ("id", "document", "score", "missing_signatures", "missing_dates", "created_at")
    list_filter = ("missing_signatures", "missing_dates")
    search_fields = ("document__filename",)
    readonly_fields = ("id", "created_at")

@admin.register(ChatHistory)
class ChatHistoryAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "document", "created_at")
    search_fields = ("user_message", "ai_response", "user__email", "document__filename")
    readonly_fields = ("id", "created_at")
