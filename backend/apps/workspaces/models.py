from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid


class Workspace(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    name = models.CharField(
        max_length=255
    )

    slug = models.SlugField(
        unique=True
    )

    is_active = models.BooleanField(
        default=True
    )

    LLM_PROVIDERS = [
        ("groq", "Groq"),
        ("openai", "OpenAI"),
        ("gemini", "Gemini")
    ]
    llm_provider = models.CharField(
        max_length=50,
        choices=LLM_PROVIDERS,
        default="groq"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        db_table = "workspaces"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name