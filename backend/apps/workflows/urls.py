from django.urls import path
from .views import WorkflowTaskListView, WorkflowTaskDetailView

urlpatterns = [
    path("", WorkflowTaskListView.as_view(), name="workflow-list"),
    path("<uuid:pk>/", WorkflowTaskDetailView.as_view(), name="workflow-detail"),
]
