from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0  # не добавлять пустые строки автоматически
    autocomplete_fields = ("product",)  # удобно, если товаров станет много
    fields = ("product", "quantity", "price_at_purchase")

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "product", "quantity", "price_at_purchase")
    search_fields = ("order__id", "product__name")

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "currency", "total_amount", "created_at")
    list_filter = ("status", "currency")
    search_fields = ("id", "user__username", "user__email")
    inlines = [OrderItemInline]