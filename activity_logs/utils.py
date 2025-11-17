from django.contrib.auth import get_user_model

from activity_logs.models import ActivityLog

User = get_user_model()


def log_activity(
    user=None,
    username=None,
    action="",
    entity_type=None,
    entity_id=None,
    details=None,
    request=None,
):
    if user and not username:
        username = user.username
    elif request and request.user.is_authenticated:
        user = request.user
        username = request.user.username
    else:
        username = username or "Anonymous"

    ip_address = None
    user_agent = None
    session_id = None

    if request:
        ip_address = request.META.get("REMOTE_ADDR")
        user_agent = request.META.get("HTTP_USER_AGENT")
        if hasattr(request, "session"):
            session_id = request.session.session_key

    ActivityLog.objects.create(
        user=user,
        username=username,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
        ip_address=ip_address,
        user_agent=user_agent,
        session_id=session_id,
    )
