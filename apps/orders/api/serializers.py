from rest_framework import serializers


class OrderItemInputSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(min_value=1)
    quantity = serializers.IntegerField(min_value=1)


class CreateOrderSerializer(serializers.Serializer):
    currency = serializers.CharField(max_length=3, default="USD")
    idempotency_key = serializers.CharField(max_length=64)
    items = OrderItemInputSerializer(many=True)