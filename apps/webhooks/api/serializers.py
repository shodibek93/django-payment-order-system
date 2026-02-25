from rest_framework import serializers


class PaymentWebhookSerializer(serializers.Serializer):
    provider = serializers.CharField(max_length=32)
    event_id = serializers.CharField(max_length=128)
    provider_payment_id = serializers.CharField(max_length=128)
    status = serializers.CharField(max_length=32)