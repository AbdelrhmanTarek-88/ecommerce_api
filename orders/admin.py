from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from .models import Order, OrderItem, ShippingAddress, OrderFees

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    autocomplete_fields = ['product_id']
    readonly_fields = ['name', 'original_price', 'discount', 'final_price', 'total']
    show_change_link = True
    can_delete = False


class ShippingAddressInline(admin.StackedInline):
    model = ShippingAddress
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'isPaid_colored', 'isDelivered_colored', 'status', 'createdAt']
    list_filter = ['isPaid', 'isDelivered', 'status', 'paymentMethod']
    search_fields = ['user__username', 'id', 'shippingAddress__address', 'paymentMethod']
    readonly_fields = ['createdAt', 'paidAt', 'deliveredAt','totalPrice']
    inlines = [OrderItemInline, ShippingAddressInline]
    actions = ['mark_delivered', 'mark_as_paid']
    autocomplete_fields = ['user']

    fieldsets = (
        ('User & Payment', {
            'fields': ('user', 'paymentMethod')
        }),
        ('Status', {
            'fields': ('isPaid', 'paidAt', 'isDelivered', 'deliveredAt', 'status')
        }),
        ('Metadata', {
            'fields': ('createdAt','totalPrice')
        }),
    )

    def isPaid_colored(self, obj):
        color = 'green' if obj.isPaid else 'red'
        return format_html(f'<strong style="color: {color};">{obj.isPaid}</strong>')
    isPaid_colored.short_description = 'Paid'

    def isDelivered_colored(self, obj):
        color = 'green' if obj.isDelivered else 'orange'
        return format_html(f'<strong style="color: {color};">{obj.isDelivered}</strong>')
    isDelivered_colored.short_description = 'Delivered'

    def mark_delivered(self, request, queryset):
        for order in queryset:
            order.isDelivered = True
            order.deliveredAt = timezone.now()
            order.status = 'delivered'
            order.save()
        self.message_user(request, f"{queryset.count()} order(s) marked as delivered.")
    mark_delivered.short_description = "Mark selected orders as Delivered"

    def mark_as_paid(self, request, queryset):
        for order in queryset:
            order.isPaid = True
            order.paidAt = timezone.now()
            order.status = 'shipped'
            order.save()
        self.message_user(request, f"{queryset.count()} order(s) marked as Paid.")
    mark_as_paid.short_description = "Mark selected orders as Paid"

@admin.register(OrderFees)
class OrderFeesAdmin(admin.ModelAdmin):
    list_display = [ 'taxRate', 'shippingPrice', 'updatedAt']
    fields = ['taxRate', 'shippingPrice']
    def has_add_permission(self, request):
        if self.model.objects.exists():
            return False
        return True