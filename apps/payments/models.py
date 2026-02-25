from django.conf import settings
from django.db import models


class Payment(models.Model):
    class Status(models.TextChoices):
        INITIATED = "INITIATED", "Initiated"
        PENDING = "PENDING", "Pending"
        SUCCEEDED = "SUCCEEDED", "Succeeded"
        FAILED = "FAILED", "Failed"
        CANCELLED = "CANCELLED", "Cancelled"

    class Provider(models.TextChoices):
        STRIPE = "STRIPE", "Stripe"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="payments")
    order = models.ForeignKey("orders.Order", on_delete=models.PROTECT, related_name="payments")

    provider = models.CharField(max_length=32, choices=Provider.choices, default=Provider.STRIPE)
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.INITIATED)

    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="USD")

    # idempotency for "initiate payment" endpoint
    idempotency_key = models.CharField(max_length=64)

    # provider identifiers
    provider_payment_id = models.CharField(max_length=128, blank=True, default="")
    provider_raw = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["provider", "user", "idempotency_key"],
                                    name="uniq_provider_user_idempotency"),
        ]
        indexes = [
            models.Index(fields=["order", "created_at"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self) -> str:
        return f"Payment#{self.pk} {self.status}"