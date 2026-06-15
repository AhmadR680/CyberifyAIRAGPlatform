import json
from django.http import StreamingHttpResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
import redis
from django.conf import settings

r = redis.Redis.from_url(settings.CELERY_BROKER_URL)

class NotificationStreamView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        def event_stream():
            pubsub = r.pubsub()
            # Subscribe to user-specific channel
            channel_name = f"user_{request.user.id}_notifications"
            pubsub.subscribe(channel_name)
            
            for message in pubsub.listen():
                if message["type"] == "message":
                    data = message["data"].decode("utf-8")
                    yield f"data: {data}\n\n"

        response = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
        response["Cache-Control"] = "no-cache"
        response["X-Accel-Buffering"] = "no"
        return response
