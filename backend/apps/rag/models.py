import uuid
from django.db import models
from pgvector.django import VectorField

class DocumentChunk(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey("documents.Document", on_delete=models.CASCADE, related_name="chunks")
    text = models.TextField()
    embedding = VectorField(dimensions=1536, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chunk {self.id} for {self.document.filename}"
