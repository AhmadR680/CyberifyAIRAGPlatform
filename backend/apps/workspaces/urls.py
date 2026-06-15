from django.urls import path
from .views import DashboardStatsView, WorkspaceSettingsView

urlpatterns = [
    path('dashboard/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('settings/', WorkspaceSettingsView.as_view(), name='workspace-settings'),
]
