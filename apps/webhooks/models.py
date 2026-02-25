from django.db import models


class WebhookEvent(models.Model):
    provider = models.CharField(max_length=32)
    event_id = models.CharField(max_length=128)
    payload = models.JSONField(default=dict, blank=True)
    processed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["provider", "event_id"], name="uniq_provider_event"),
        ]
        indexes = [
            models.Index(fields=["provider", "event_id"]),
        ]

    def __str__(self) -> str:
        return f"{self.provider}:{self.event_id}"