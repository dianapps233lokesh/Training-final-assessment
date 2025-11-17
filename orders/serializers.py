from rest_framework import serializers

from orders.models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source="product.name")

    class Meta:
        model = OrderItem
        fields = ["id", "product", "product_name", "quantity", "price", "subtotal"]
        read_only_fields = ["price", "subtotal"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "order_number",
            "user",
            "status",
            "total_amount",
            "shipping_address",
            "payment_method",
            "payment_status",
            "ordered_at",
            "updated_at",
            "delivered_at",
            "items",
        ]
        read_only_fields = [
            "order_number",
            "user",
            "status",
            "total_amount",
            "payment_status",
            "ordered_at",
            "updated_at",
            "delivered_at",
        ]

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        total_amount = 0
        order_items = []

        for item_data in items_data:
            product = item_data["product"]
            quantity = item_data["quantity"]

            if product.stock_quantity < quantity:
                raise serializers.ValidationError(
                    f"Not enough stock for product {product.name}. Available: {product.stock_quantity}"
                )

            price = product.price
            subtotal = price * quantity
            total_amount += subtotal

            order_items.append(
                OrderItem(
                    product=product, quantity=quantity, price=price, subtotal=subtotal
                )
            )

        validated_data["total_amount"] = total_amount
        validated_data["user"] = self.context["request"].user
        order = Order.objects.create(**validated_data)

        for order_item in order_items:
            order_item.order = order
            order_item.save()
            # Decrease stock quantity
            order_item.product.stock_quantity -= order_item.quantity
            order_item.product.save()

        return order
