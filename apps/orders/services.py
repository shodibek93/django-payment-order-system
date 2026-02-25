from __future__ import annotations

from decimal import Decimal
from typing import Iterable, TypedDict

from django.db import transaction, IntegrityError

from apps.catalog.models import Product
from .models import Order, OrderItem


class CreateOrderItem(TypedDict):
    product_id: int
    quantity: int


@transaction.atomic
def create_order(*, user, items, currency="USD", idempotency_key: str):
    """
    Creates an order with items in a single transaction.

    Idempotency:
      - If the same idempotency_key is used again, returns the existing order.
      - Protects from duplicate orders on retries/timeouts.
    """
    # 1) Idempotency check
    existing = Order.objects.filter(idempotency_key=idempotency_key).select_for_update().first()
    if existing:
        return existing

    # 2) Create order (draft initially)
    try:
        order = Order.objects.create(
            user=user,
            status=Order.Status.DRAFT,
            currency=currency,
            total_amount=Decimal("0.00"),
            idempotency_key=idempotency_key,
        )
    except IntegrityError:
        # Someone created it in parallel
        return Order.objects.get(idempotency_key=idempotency_key)

    # 3) Load products in bulk (avoid N+1)
    items_list = list(items)
    product_ids = [i["product_id"] for i in items_list]
    products = {p.id: p for p in Product.objects.filter(id__in=product_ids, is_active=True)}

    # 4) Validate + create items
    total = Decimal("0.00")

    order_items: list[OrderItem] = []
    for i in items_list:
        pid = int(i["product_id"])
        qty = int(i["quantity"])

        if qty <= 0:
            raise ValueError(f"Invalid quantity: {qty}")

        product = products.get(pid)
        if not product:
            raise ValueError(f"Product not found or inactive: {pid}")

        price = product.price
        line_total = price * qty
        total += line_total

        order_items.append(
            OrderItem(
                order=order,
                product=product,
                quantity=qty,
                price_at_purchase=price,
            )
        )

    OrderItem.objects.bulk_create(order_items)

    # 5) Update totals & status
    order.total_amount = total
    order.status = Order.Status.PENDING_PAYMENT if total > 0 else Order.Status.DRAFT
    order.save(update_fields=["total_amount", "status"])

    return order