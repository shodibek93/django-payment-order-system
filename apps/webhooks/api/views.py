from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from apps.webhooks.security import verify_signature
from apps.webhooks.services import process_payment_webhook
from .serializers import PaymentWebhookSerializer
from rest_framework.exceptions import ValidationError


class PaymentWebhookAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        signature = request.headers.get("X-Webhook-Signature", "")
        timestamp = request.headers.get("X-Webhook-Timestamp", "")

        if not verify_signature(body=request.body, header_signature=signature, header_timestamp=timestamp):
            return Response({"detail": "Invalid webhook signature"}, status=status.HTTP_401_UNAUTHORIZED)

        s = PaymentWebhookSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        data = s.validated_data

        try:
            result = process_payment_webhook(
                provider=data["provider"],
                event_id=data["event_id"],
                provider_payment_id=data["provider_payment_id"],
                status=data["status"],
                payload=request.data,
            )
        except ValueError as e:
            raise ValidationError({"detail": str(e)})

        return Response(result)