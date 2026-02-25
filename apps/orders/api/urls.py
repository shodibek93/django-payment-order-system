from django.urls import path
from .views import CreateOrderAPIView

urlpatterns = [
    path("orders/", CreateOrderAPIView.as_view(), name="create-order"),
]