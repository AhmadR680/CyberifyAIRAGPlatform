from rest_framework import serializers
from .models import ContractAnalysis, ComplianceScore, ChatHistory

class ContractAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractAnalysis
        fields = "__all__"

class ComplianceScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplianceScore
        fields = "__all__"

class ChatHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatHistory
        fields = "__all__"
        read_only_fields = ["id", "document", "user", "ai_response", "created_at"]
