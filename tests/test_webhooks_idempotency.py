import json
import time
import pytest

from apps.webhooks.security import build_signature

pytestmark = pytest.mark.django_db


def _send(api_client, payload: dict):
    body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    ts = str(int(time.time()))
    sig = build_signature(body=body, timestamp=ts)
    return api_client.post(
        "/api/webhooks/payment/",
        data=body,
        content_type="application/json",
        **{
            "HTTP_X_WEBHOOK_SIGNATURE": sig,
            "HTTP_X_WEBHOOK_TIMESTAMP": ts,
        }
    )


def test_webhook_event_id_idempotency(api_client, payment_initiated):
    payload = {
        "provider": "STRIPE",
        "event_id": "evt_dup_1",
        "provider_payment_id": payment_initiated.provider_payment_id,
        "status": "SUCCEEDED",
    }

    r1 = _send(api_client, payload)
    assert r1.status_code == 200
    assert r1.data["duplicate"] is False

    r2 = _send(api_client, payload)
    assert r2.status_code == 200
    assert r2.data["duplicate"] is True