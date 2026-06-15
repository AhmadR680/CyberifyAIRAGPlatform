import uuid
from django.db import models

class ContractAnalysis(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.OneToOneField("documents.Document", on_delete=models.CASCADE, related_name="contract_analysis")
    summary = models.TextField(blank=True, null=True)
    risks = models.JSONField(default=list)
    missing_clauses = models.JSONField(default=list)
    recommendations = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

class ComplianceScore(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.OneToOneField("documents.Document", on_delete=models.CASCADE, related_name="compliance_score")
    score = models.IntegerField(default=0)
    issues = models.JSONField(default=list)
    missing_signatures = models.BooleanField(default=False)
    missing_dates = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class ChatHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey("documents.Document", on_delete=models.CASCADE, related_name="chat_history")
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="chat_history")
    user_message = models.TextField()
    ai_response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
