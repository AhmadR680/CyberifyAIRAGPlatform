from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import WorkflowTask
from .serializers import WorkflowTaskSerializer

class WorkflowTaskListView(generics.ListCreateAPIView):
    serializer_class = WorkflowTaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return WorkflowTask.objects.filter(document__workspace=self.request.user.workspace)

class WorkflowTaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = WorkflowTaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return WorkflowTask.objects.filter(document__workspace=self.request.user.workspace)
