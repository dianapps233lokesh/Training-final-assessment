from datetime import timedelta

from django.db import models
from django.db.models import Count, Sum
from django.db.models.functions import TruncDay, TruncMonth, TruncWeek
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.choices import UserType
from authentication.models import UserProfile
from orders.models import Order, OrderItem
from products.models import Product


class DashboardOverviewAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.user_type == UserType.ADMIN.value:
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )
        today = timezone.now().date()

        total_orders = Order.objects.count()
        total_revenue = (
            Order.objects.filter(status="delivered").aggregate(Sum("total_amount"))[
                "total_amount__sum"
            ]
            or 0
        )
        pending_orders = Order.objects.filter(status="pending").count()
        delivered_orders = Order.objects.filter(status="delivered").count()
        total_customers = UserProfile.objects.filter(user_type="CUSTOMER").count()
        active_products = Product.objects.filter(is_active=True).count()
        low_stock_products = Product.objects.filter(
            stock_quantity__lte=models.F("low_stock_threshold")
        ).count()
        today_revenue = (
            Order.objects.filter(ordered_at__date=today, status="delivered").aggregate(
                Sum("total_amount")
            )["total_amount__sum"]
            or 0
        )
        today_orders = Order.objects.filter(ordered_at__date=today).count()

        data = {
            "total_orders": total_orders,
            "total_revenue": total_revenue,
            "pending_orders": pending_orders,
            "delivered_orders": delivered_orders,
            "total_customers": total_customers,
            "active_products": active_products,
            "low_stock_products": low_stock_products,
            "today_revenue": today_revenue,
            "today_orders": today_orders,
        }
        return Response(data)


class SalesAnalyticsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.user_type == UserType.ADMIN.value:
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )
        period = request.query_params.get("period", "daily")  # daily, weekly, monthly

        if period == "daily":
            sales_data = (
                Order.objects.annotate(day=TruncDay("ordered_at"))
                .values("day")
                .annotate(total_orders=Count("id"), total_revenue=Sum("total_amount"))
                .order_by("day")
            )
        elif period == "weekly":
            sales_data = (
                Order.objects.annotate(week=TruncWeek("ordered_at"))
                .values("week")
                .annotate(total_orders=Count("id"), total_revenue=Sum("total_amount"))
                .order_by("week")
            )
        elif period == "monthly":
            sales_data = (
                Order.objects.annotate(month=TruncMonth("ordered_at"))
                .values("month")
                .annotate(total_orders=Count("id"), total_revenue=Sum("total_amount"))
                .order_by("month")
            )
        else:
            return Response(
                {"detail": "Invalid period. Choose from 'daily', 'weekly', 'monthly'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(sales_data)


class TopSellingProductsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.user_type == UserType.ADMIN.value:
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )
        top_products = (
            OrderItem.objects.values("product__name")
            .annotate(total_quantity_sold=Sum("quantity"))
            .order_by("-total_quantity_sold")[:10]
        )
        return Response(top_products)


class RevenueTrendsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Example: Last 30 days revenue trend
        if not request.user.user_type == UserType.ADMIN.value:
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)

        revenue_trend = (
            Order.objects.filter(
                ordered_at__date__range=[start_date, end_date], status="delivered"
            )
            .annotate(day=TruncDay("ordered_at"))
            .values("day")
            .annotate(daily_revenue=Sum("total_amount"))
            .order_by("day")
        )
        return Response(revenue_trend)


class OrderStatusDistributionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.user_type == UserType.ADMIN.value:
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )
        status_distribution = (
            Order.objects.values("status")
            .annotate(count=Count("status"))
            .order_by("status")
        )
        return Response(status_distribution)
