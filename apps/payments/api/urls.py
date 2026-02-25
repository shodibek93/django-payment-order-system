from django.urls import path
from .views import InitiatePaymentAPIView

urlpatterns = [
    path("payments/", InitiatePaymentAPIView.as_view(), name="initiate-payment"),
]