import uuid

from django.db import models


class Document(models.Model):

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    workspace = models.ForeignKey(
        "workspaces.Workspace",
        on_delete=models.CASCADE,
        related_name="documents"
    )

    uploaded_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE
    )

    file = models.FileField(
        upload_to="documents/"
    )

    filename = models.CharField(
        max_length=255
    )

    content_type = models.CharField(
        max_length=100
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    extracted_text = models.TextField(
        blank=True,
        null=True
    )

    metadata = models.JSONField(
        default=dict
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.filename