from __future__ import annotations

from django.db import IntegrityError, transaction

from apps.audit.services import write_audit
from apps.orders.models import Order
from apps.payments.models import Payment
from .models import WebhookEvent


@transaction.atomic
def process_payment_webhook(*, provider: str, event_id: str, provider_payment_id: str, status: str, payload: dict) -> dict:
    # 1) Idempotency on event_id
    try:
        with transaction.atomic():
            WebhookEvent.objects.create(
                provider=provider,
                event_id=event_id,
                payload=payload or {}
            )
    except IntegrityError:
        payment = Payment.objects.filter(
            provider=provider,
            provider_payment_id=provider_payment_id
        ).select_related("order").first()

        if not payment:
            return {"ok": True, "duplicate": True, "missing_payment": True}

        return {
            "ok": True,
            "duplicate": True,
            "payment_id": payment.id,
            "order_id": payment.order_id,
            "payment_status": payment.status,
            "order_status": payment.order.status,
        }

    # 2) Lock payment row
    payment = (
        Payment.objects.select_for_update()
        .select_related("order")
        .get(provider=provider, provider_payment_id=provider_payment_id)
    )

    # 3) Update payment status
    new_status = status.upper()
    if new_status not in Payment.Status.values:
        raise ValueError(f"Unknown payment status: {new_status}")

    payment.status = new_status
    payment.provider_raw = payload or {}
    payment.save(update_fields=["status", "provider_raw"])

    # 4) Update order based on payment result
    order = payment.order
    if new_status == Payment.Status.SUCCEEDED:
        order.status = Order.Status.PAID
        order.save(update_fields=["status"])
    elif new_status in (Payment.Status.FAILED, Payment.Status.CANCELLED):
        order.status = Order.Status.CANCELLED
        order.save(update_fields=["status"])

    # 5) Audit (user берём из payment.user)
    write_audit(
        user=payment.user,
        action="WEBHOOK_PAYMENT_STATUS",
        entity_type="payment",
        entity_id=str(payment.id),
        payload={
            "provider": provider,
            "event_id": event_id,
            "provider_payment_id": provider_payment_id,
            "new_status": new_status,
        },
    )

    return {"ok": True, "duplicate": False, "payment_id": payment.id, "order_id": order.id, "payment_status": payment.status, "order_status": order.status}