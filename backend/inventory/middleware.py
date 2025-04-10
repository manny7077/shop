from django.utils import timezone
from .utils.audit_logger import log_action

class AuditLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.user.is_authenticated:
            log_action(
                request,
                action='VIEW',
                details={'method': request.method, 'path': request.path}
            )

        return response