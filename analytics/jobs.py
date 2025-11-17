import logging
from datetime import timedelta

from django.db.models import Sum
from django.utils import timezone

from activity_logs.utils import log_activity
from analytics.models import DailySales
from orders.models import Order
from products.models import Product

logger = logging.getLogger(__name__)


def daily_sales_aggregation_job():
    logger.info("Running daily_sales_aggregation_job...")
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)

    # Filter delivered orders for yesterday
    orders_yesterday = Order.objects.filter(
        ordered_at__date=yesterday, status="delivered"
    )

    total_orders = orders_yesterday.count()
    total_revenue = (
        orders_yesterday.aggregate(Sum("total_amount"))["total_amount__sum"] or 0
    )
    total_items_sold = (
        orders_yesterday.aggregate(Sum("items__quantity"))["items__quantity__sum"] or 0
    )
    average_order_value = total_revenue / total_orders if total_orders > 0 else 0

    daily_sales, created = DailySales.objects.update_or_create(
        date=yesterday,
        defaults={
            "total_orders": total_orders,
            "total_revenue": total_revenue,
            "total_items_sold": total_items_sold,
            "average_order_value": average_order_value,
        },
    )
    logger.info(
        f"Aggregated sales for {yesterday}: {daily_sales.total_revenue} (Orders: {daily_sales.total_orders})"
    )


def low_stock_alert_job():
    logger.info("Running low_stock_alert_job...")
    low_stock_products = Product.objects.filter(
        stock_quantity__lte=models.F("low_stock_threshold")
    )
    count = low_stock_products.count()

    if count > 0:
        log_activity(
            action="low_stock_alert",
            entity_type="system",
            details={
                "count": count,
                "products": list(low_stock_products.values_list("name", flat=True)),
            },
        )
        logger.warning(f"Low stock alert: {count} products")
    else:
        logger.info("No low stock products found.")


def pending_order_reminder_job():
    logger.info("Running pending_order_reminder_job...")
    twenty_four_hours_ago = timezone.now() - timedelta(hours=24)
    pending_orders = Order.objects.filter(
        status="pending", ordered_at__lte=twenty_four_hours_ago
    )
    count = pending_orders.count()

    if count > 0:
        log_activity(
            action="pending_order_reminder",
            entity_type="system",
            details={
                "count": count,
                "orders": list(pending_orders.values_list("order_number", flat=True)),
            },
        )
        logger.info(f"Found {count} pending orders older than 24 hours.")
    else:
        logger.info("No pending orders older than 24 hours found.")
