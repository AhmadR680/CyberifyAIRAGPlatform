from rest_framework import generics
from rest_framework.permissions import (
    IsAuthenticated
)

from .models import Document
from .serializers import (
    DocumentUploadSerializer,
    DocumentSerializer
)

from .tasks import process_document


class DocumentUploadView(
    generics.CreateAPIView
):
    serializer_class = (
        DocumentUploadSerializer
    )

    permission_classes = [
        IsAuthenticated
    ]

    def perform_create(
        self,
        serializer
    ):
        document = serializer.save(
            workspace=self.request.user.workspace,
            uploaded_by=self.request.user,
            filename=self.request.FILES[
                "file"
            ].name,
            content_type=self.request.FILES[
                "file"
            ].content_type,
        )

        process_document.delay(
            str(document.id)
        )


class DocumentListView(
    generics.ListAPIView
):
    serializer_class = DocumentSerializer
    permission_classes = [
        IsAuthenticated
    ]

    def get_queryset(self):
        return Document.objects.filter(
            workspace=self.request.user.workspace
        )