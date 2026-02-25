from rest_framework import serializers


class InitiatePaymentSerializer(serializers.Serializer):
    order_id = serializers.IntegerField(min_value=1)
    idempotency_key = serializers.CharField(max_length=64)