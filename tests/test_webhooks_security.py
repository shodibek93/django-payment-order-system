import json
import time
import pytest

from apps.webhooks.security import build_signature
from apps.payments.models import Payment
from apps.orders.models import Order

pytestmark = pytest.mark.django_db


def _json_bytes(d: dict) -> bytes:
    # ВАЖНО: стабильно (без пробелов) чтобы подпись совпадала
    return json.dumps(d, separators=(",", ":")).encode("utf-8")


def test_webhook_requires_signature(api_client):
    r = api_client.post("/api/webhooks/payment/", {"x": 1}, format="json")
    assert r.status_code == 401


def test_webhook_valid_signature_ok(api_client, payment_initiated, order_pending):
    body_dict = {
        "provider": "STRIPE",
        "event_id": "evt_sig_100",
        "provider_payment_id": payment_initiated.provider_payment_id,
        "status": "SUCCEEDED",
    }
    body = _json_bytes(body_dict)
    ts = str(int(time.time()))
    sig = build_signature(body=body, timestamp=ts)

    r = api_client.post(
        "/api/webhooks/payment/",
        data=body,
        content_type="application/json",
        **{
            "HTTP_X_WEBHOOK_SIGNATURE": sig,
            "HTTP_X_WEBHOOK_TIMESTAMP": ts,
        }
    )
    assert r.status_code == 200

    payment_initiated.refresh_from_db()
    order_pending.refresh_from_db()
    assert payment_initiated.status == Payment.Status.SUCCEEDED
    assert order_pending.status == Order.Status.PAID