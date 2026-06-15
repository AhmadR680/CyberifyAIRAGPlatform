from rest_framework import serializers

from .models import Document


class DocumentUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ["file"]

    def validate_file(self,file):
        allowed = ["application/pdf", "text/plain", "application/vnd.openxmlformats-officedocument.wordprocessingml.document",]

        if file.content_type not in allowed:
            raise serializers.ValidationError("Unsupported file type.")

        return file
    
class DocumentSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = Document
        fields = "__all__"