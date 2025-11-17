from django.db import transaction
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from activity_logs.utils import log_activity
from authentication.choices import UserType
from orders.choices import OrderStatusChoices
from orders.models import Order
from orders.serializers import OrderSerializer


class OrderListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = OrderSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        log_activity(
            user=request.user,
            action="order_created",
            entity_type="order",
            entity_id=order.id,
            details=serializer.data,
            request=request,
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class OrderRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, id, user):
        try:
            order = Order.objects.get(id=id)
            if order.user != user and not user.user_type == UserType.ADMIN.value:
                raise status.HTTP_403_FORBIDDEN
            return order
        except Order.DoesNotExist:
            raise status.HTTP_404_NOT_FOUND

    def get(self, request, id):
        order = self.get_object(id, request.user)
        serializer = OrderSerializer(order)
        return Response(serializer.data)


class OrderStatusUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, id):
        if not request.user.user_type == UserType.ADMIN.value:
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )
        try:
            order = Order.objects.get(id=id)
        except Order.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        old_status = order.status
        new_status = request.data.get("status")
        if new_status not in OrderStatusChoices.values:
            return Response(
                {"detail": "Invalid status provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        order.status = new_status
        order.save()
        serializer = OrderSerializer(order)
        log_activity(
            user=request.user,
            action="order_status_updated",
            entity_type="order",
            entity_id=order.id,
            details={"old_status": old_status, "new_status": new_status},
            request=request,
        )
        return Response(serializer.data)


class AdminOrderListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.user_type == UserType.ADMIN.value:
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )
        orders = Order.objects.all()
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)


class OrderCancelAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, id):
        try:
            order = Order.objects.get(id=id)
        except Order.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if order.user != request.user:
            return Response(
                {"detail": "You do not have permission to cancel this order."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if order.status != OrderStatusChoices.PENDING:
            return Response(
                {"detail": "Only pending orders can be cancelled."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            order.status = OrderStatusChoices.CANCELLED
            order.save()
            # Restore stock quantity
            for item in order.items.all():
                item.product.stock_quantity += item.quantity
                item.product.save()
        log_activity(
            user=request.user,
            action="order_cancelled",
            entity_type="order",
            entity_id=order.id,
            details={"order_number": order.order_number},
            request=request,
        )
        return Response(status=status.HTTP_204_NO_CONTENT)
