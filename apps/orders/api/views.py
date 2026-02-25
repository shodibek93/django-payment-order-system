from django.db import IntegrityError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.orders.models import Order
from apps.orders.services import create_order
from .serializers import CreateOrderSerializer


class CreateOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # 100% idempotency behavior even under race conditions:
        try:
            order = create_order(
                user=request.user,
                currency=data["currency"],
                idempotency_key=data["idempotency_key"],
                items=data["items"],
            )
        except IntegrityError:
            # If created concurrently, return existing order for this user+key
            order = Order.objects.get(user=request.user, idempotency_key=data["idempotency_key"])

        return Response(
            {
                "id": order.id,
                "status": order.status,
                "currency": order.currency,
                "total_amount": str(order.total_amount),
            },
            status=status.HTTP_201_CREATED,
        )