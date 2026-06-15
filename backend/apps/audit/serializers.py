from rest_framework import serializers
from .models import AuditLog

class AuditLogSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = AuditLog
        fields = ["id", "workspace", "user", "user_email", "action", "resource_type", "resource_id", "details", "created_at"]
