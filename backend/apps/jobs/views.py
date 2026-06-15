from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from celery.app.control import Inspect
from config.celery import app

class JobDashboardStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        i = Inspect(app=app)
        
        try:
            active_tasks = i.active() or {}
            reserved_tasks = i.reserved() or {}
            scheduled_tasks = i.scheduled() or {}
            
            stats = {
                "active": sum(len(tasks) for tasks in active_tasks.values()),
                "queued": sum(len(tasks) for tasks in reserved_tasks.values()),
                "scheduled": sum(len(tasks) for tasks in scheduled_tasks.values()),
            }
        except Exception:
            # If celery workers are down
            stats = {"active": 0, "queued": 0, "scheduled": 0, "error": "Could not connect to Celery workers"}

        return Response(stats)
