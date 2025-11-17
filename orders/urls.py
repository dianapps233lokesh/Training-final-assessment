from django.urls import path

from orders.views import (
    AdminOrderListAPIView,
    OrderCancelAPIView,
    OrderListCreateAPIView,
    OrderRetrieveAPIView,
    OrderStatusUpdateAPIView,
)

urlpatterns = [
    path("", OrderListCreateAPIView.as_view(), name="order-list-create"),
    path("<int:id>/", OrderRetrieveAPIView.as_view(), name="order-detail"),
    path(
        "<int:id>/status/",
        OrderStatusUpdateAPIView.as_view(),
        name="order-status-update",
    ),
    path("admin/all/", AdminOrderListAPIView.as_view(), name="admin-order-list"),
    path("<int:id>/cancel/", OrderCancelAPIView.as_view(), name="order-cancel"),
]
