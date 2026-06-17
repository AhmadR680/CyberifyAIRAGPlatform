import json
from django.http import StreamingHttpResponse
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
import redis
from django.conf import settings
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

r = redis.Redis.from_url(settings.CELERY_BROKER_URL)

class NotificationStreamView(APIView):
    # Use AllowAny because we are manually checking the query param token
    permission_classes = [AllowAny]

    def get(self, request):
        token = request.query_params.get("token")
        if not token:
            return StreamingHttpResponse("Unauthorized", status=401)
            
        try:
            jwt_auth = JWTAuthentication()
            validated_token = jwt_auth.get_validated_token(token)
            user = jwt_auth.get_user(validated_token)
        except (InvalidToken, TokenError):
            return StreamingHttpResponse("Unauthorized", status=401)

        def event_stream(user_id):
            pubsub = r.pubsub()
            # Subscribe to user-specific channel
            channel_name = f"user_{user_id}_notifications"
            pubsub.subscribe(channel_name)
            
            for message in pubsub.listen():
                if message["type"] == "message":
                    data = message["data"].decode("utf-8")
                    yield f"data: {data}\n\n"

        response = StreamingHttpResponse(event_stream(user.id), content_type="text/event-stream")
        response["Cache-Control"] = "no-cache"
        response["X-Accel-Buffering"] = "no"
        return response
