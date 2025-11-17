from django.urls import path

from analytics.views import (
    DashboardOverviewAPIView,
    OrderStatusDistributionAPIView,
    RevenueTrendsAPIView,
    SalesAnalyticsAPIView,
    TopSellingProductsAPIView,
)

urlpatterns = [
    path("dashboard/", DashboardOverviewAPIView.as_view(), name="dashboard-overview"),
    path("sales/", SalesAnalyticsAPIView.as_view(), name="sales-analytics"),
    path(
        "products/top-selling/",
        TopSellingProductsAPIView.as_view(),
        name="top-selling-products",
    ),
    path("revenue/", RevenueTrendsAPIView.as_view(), name="revenue-trends"),
    path(
        "orders/status-distribution/",
        OrderStatusDistributionAPIView.as_view(),
        name="order-status-distribution",
    ),
]
