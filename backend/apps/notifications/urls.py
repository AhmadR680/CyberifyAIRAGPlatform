from django.urls import path
from .views import NotificationStreamView

urlpatterns = [
    path("stream/", NotificationStreamView.as_view(), name="notification-stream"),
]
