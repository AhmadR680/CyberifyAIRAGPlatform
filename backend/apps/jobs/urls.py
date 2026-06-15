from django.urls import path
from .views import JobDashboardStatsView

urlpatterns = [
    path("dashboard/", JobDashboardStatsView.as_view(), name="job-dashboard"),
]
