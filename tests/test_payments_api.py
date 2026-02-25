import pytest
from apps.payments.models import Payment
from apps.orders.models import Order

pytestmark = pytest.mark.django_db


def test_initiate_payment_idempotency(auth_client, order_pending):
    payload = {"order_id": order_pending.id, "idempotency_key": "pay-xyz"}

    r1 = auth_client.post("/api/payments/", payload, format="json")
    assert r1.status_code in (200, 201)
    pid1 = r1.data["id"]

    r2 = auth_client.post("/api/payments/", payload, format="json")
    assert r2.status_code in (200, 201)
    pid2 = r2.data["id"]

    assert pid1 == pid2
    assert Payment.objects.filter(id=pid1).count() == 1


def test_cannot_pay_non_pending_order(auth_client, order_pending):
    order_pending.status = Order.Status.CANCELLED
    order_pending.save(update_fields=["status"])

    r = auth_client.post("/api/payments/", {"order_id": order_pending.id, "idempotency_key": "pay-1"}, format="json")
    assert r.status_code == 400
    assert "cannot be paid" in str(r.data).lower()