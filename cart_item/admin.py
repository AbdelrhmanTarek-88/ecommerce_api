from django.contrib import admin
from .models import CartItem

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'total_price', 'added_at')
    list_filter = ['added_at']
    search_fields = ('user__username', 'product__name')
    ordering = ('-added_at',)
    list_per_page = 25

    def total_price(self, obj):
        return f"{obj.quantity * obj.product.price} $"
    total_price.short_description = 'Total Price'
