
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

from orders.choices import OrderStatusChoices, PaymentStatusChoices

User = get_user_model()


class Order(models.Model):
    order_number = models.CharField(max_length=50, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")

    status = models.CharField(
        max_length=20, choices=OrderStatusChoices, default="pending"
    )

    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_address = models.TextField()

    payment_method = models.CharField(max_length=50)

    payment_status = models.CharField(
        max_length=20, choices=PaymentStatusChoices, default="pending"
    )

    ordered_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Order #{self.order_number}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            today = timezone.now().strftime("%Y%m%d")
            # Get the count of orders for today
            today_orders_count = (
                Order.objects.filter(ordered_at__date=timezone.now().date()).count() + 1
            )
            self.order_number = f"ORD-{today}-{today_orders_count:03d}"
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE)

    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
