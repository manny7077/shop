
from ..models import AuditLog
from django.contrib.auth import get_user_model
from ipware import get_client_ip

def log_action(request, action, model=None, object_id=None, details=None, user=None):
    User = get_user_model()
    # Use provided user if given, otherwise fall back to request.user
    log_user = user if user is not None else (request.user if request.user.is_authenticated else None)
    ip, _ = get_client_ip(request)
    
    AuditLog.objects.create(
        user=log_user,
        action=action,
        model=model,
        object_id=object_id,
        details=details or {},
        ip_address=ip
    )