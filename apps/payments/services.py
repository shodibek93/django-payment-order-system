from __future__ import annotations

import uuid
from django.db import IntegrityError, transaction

from apps.orders.models import Order
from .models import Payment


@transaction.atomic
def initiate_payment(*, user, order_id: int, idempotency_key: str) -> Payment:
    # 1) Find order (only user's)
    order = (
        Order.objects
        .select_for_update()
        .get(id=order_id, user=user)
    )

    # 2) Basic state check
    if order.status != Order.Status.PENDING_PAYMENT:
        raise ValueError(f"Order cannot be paid in status: {order.status}")

    # 3) Idempotency: try find existing payment for this user+provider+key
    existing = Payment.objects.filter(
        user=user,
        provider=Payment.Provider.STRIPE,
        idempotency_key=idempotency_key,
    ).first()
    if existing:
        return existing

    # 4) Create payment (stub)
    try:
        payment = Payment.objects.create(
            user=user,
            order=order,
            provider=Payment.Provider.STRIPE,
            status=Payment.Status.INITIATED,
            amount=order.total_amount,
            currency=order.currency,
            idempotency_key=idempotency_key,
            provider_payment_id=f"stub_{uuid.uuid4().hex}",
            provider_raw={},          # later store provider response
        )
    except IntegrityError:
        # created in parallel
        return Payment.objects.get(
            user=user,
            provider=Payment.Provider.STRIPE,
            idempotency_key=idempotency_key,
        )

    return payment