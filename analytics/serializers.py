from rest_framework import serializers

from analytics.models import DailySales


class DailySalesSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailySales
        fields = "__all__"
