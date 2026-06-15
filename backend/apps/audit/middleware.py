import json
from .models import AuditLog

class AuditLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Only log authenticated requests and modify actions
        if request.user.is_authenticated and request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            action = f"{request.method} {request.path}"
            resource_type = request.path.split("/")[2] if len(request.path.split("/")) > 2 else "unknown"
            
            AuditLog.objects.create(
                workspace=getattr(request.user, "workspace", None),
                user=request.user,
                action=action,
                resource_type=resource_type,
                details={"status_code": response.status_code}
            )

        return response
