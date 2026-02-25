from django.urls import path
from .views import PaymentWebhookAPIView

urlpatterns = [
    path("webhooks/payment/", PaymentWebhookAPIView.as_view(), name="payment-webhook"),
]