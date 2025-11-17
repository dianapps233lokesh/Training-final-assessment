from rest_framework import serializers

from activity_logs.models import ActivityLog


class ActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityLog
        fields = "__all__"
        read_only_fields = ["user", "username", "timestamp"]
