from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.payments.services import initiate_payment
from .serializers import InitiatePaymentSerializer
from rest_framework.exceptions import ValidationError


class InitiatePaymentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = InitiatePaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            payment = initiate_payment(
                user=request.user,
                order_id=data["order_id"],
                idempotency_key=data["idempotency_key"],
            )
        except ValueError as e:
            raise ValidationError({"detail": str(e)})

        return Response(
            {
                "id": payment.id,
                "status": payment.status,
                "order_id": payment.order_id,
                "amount": str(payment.amount),
                "currency": payment.currency,
                "provider_payment_id": payment.provider_payment_id,
            },
            status=status.HTTP_201_CREATED,
        )