import uuid
from django.db import models

class WorkflowTask(models.Model):
    class Status(models.TextChoices):
        TODO = "todo", "To Do"
        IN_PROGRESS = "in_progress", "In Progress"
        DONE = "done", "Done"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey("documents.Document", on_delete=models.CASCADE, related_name="workflow_tasks")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    assignee = models.CharField(max_length=100, blank=True, null=True)
    deadline = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.TODO)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
