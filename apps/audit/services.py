from apps.audit.models import AuditLog


def write_audit(*, user, action: str, entity_type: str, entity_id: str, payload: dict) -> None:
    AuditLog.objects.create(
        user=user,
        action=action,
        entity_type=entity_type,
        entity_id=str(entity_id),
        payload=payload or {},
    )