from django.urls import path

from activity_logs.views import ActivityLogListCreateAPIView, UserActivityLogListAPIView

urlpatterns = [
    path("", ActivityLogListCreateAPIView.as_view(), name="activity-log-list-create"),
    path(
        "user/<int:user_id>/",
        UserActivityLogListAPIView.as_view(),
        name="user-activity-log-list",
    ),
]
