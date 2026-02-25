import pytest
from django.contrib.auth import get_user_model

from apps.orders.models import Order
from apps.payments.models import Payment


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def user():
    User = get_user_model()
    return User.objects.create_user(username="u1", password="pass12345")


@pytest.fixture
def auth_client(api_client, user):
    api_client.login(username="u1", password="pass12345")
    return api_client


@pytest.fixture
def order_pending(user):
    return Order.objects.create(
        user=user,
        status=Order.Status.PENDING_PAYMENT,
        currency="USD",
        total_amount="21.00",
        idempotency_key="ord-1",
    )


@pytest.fixture
def payment_initiated(user, order_pending):
    return Payment.objects.create(
        user=user,
        order=order_pending,
        provider=Payment.Provider.STRIPE,
        status=Payment.Status.INITIATED,
        amount=order_pending.total_amount,
        currency=order_pending.currency,
        idempotency_key="pay-1",
        provider_payment_id="stub_test_001",
        provider_raw={},
    )