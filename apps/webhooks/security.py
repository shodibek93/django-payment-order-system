import hashlib
import hmac
import time

from django.conf import settings
from django.utils.crypto import constant_time_compare


def build_signature(*, body: bytes, timestamp: str) -> str:
    secret = getattr(settings, "WEBHOOK_SECRET", "")
    if not secret:
        raise RuntimeError("WEBHOOK_SECRET is not set")

    msg = timestamp.encode("utf-8") + b"." + body
    digest = hmac.new(
        key=secret.encode("utf-8"),
        msg=msg,
        digestmod=hashlib.sha256,
    ).hexdigest()
    return f"sha256={digest}"


def verify_signature(*, body: bytes, header_signature: str, header_timestamp: str) -> bool:
    if not header_timestamp:
        return False

    # replay protection
    try:
        ts = int(header_timestamp)
    except ValueError:
        return False

    now = int(time.time())
    tolerance = getattr(settings, "WEBHOOK_TOLERANCE_SECONDS", 300)
    if abs(now - ts) > tolerance:
        return False

    try:
        expected = build_signature(body=body, timestamp=header_timestamp)
    except RuntimeError:
        return False

    return constant_time_compare(expected, header_signature or "")