from rest_framework import serializers
from .models import WorkflowTask

class WorkflowTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkflowTask
        fields = "__all__"
