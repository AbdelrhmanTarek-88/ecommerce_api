from rest_framework import serializers
from .models import Order, OrderItem, ShippingAddress, OrderFees
from users.serializers import UserPublicSerializer
from decimal import Decimal

class OrderItemSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    product_id = serializers.IntegerField(source='product.id', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product_id', 'name', 'qty', 'original_price', 'discount', 'final_price', 'total', 'image']

    def get_image(self, obj):
        request = self.context.get('request')
        product = obj.product
        if not product or not request:
            return ''
        
        if product.image_field:
            try:
                return request.build_absolute_uri(product.image_field.url)
            except:
                pass
        if product.image_url:
            return request.build_absolute_uri(product.image_url)
        
        return ''



class ShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields = ['address', 'postalCode', 'city', 'country', 'phone']
        extra_kwargs = {
            'address': {'required': False},
            'city': {'required': False},
            'postalCode': {'required': False},
            'country': {'required': False},
            'phone': {'required': False},
        }


class OrderSerializer(serializers.ModelSerializer):
    orderItems = OrderItemSerializer(many=True, read_only=True)
    shippingAddress = ShippingAddressSerializer(read_only=True)
    user = UserPublicSerializer(read_only=True)
    taxPrice = serializers.SerializerMethodField()
    shippingPrice = serializers.SerializerMethodField()
    formatted_created_at = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'user',
            'paymentMethod',
            'totalPrice',
            'taxPrice',
            'shippingPrice',
            'isPaid',
            'paidAt',
            'isDelivered',
            'deliveredAt',
            'formatted_created_at',
            'status',
            'orderItems',
            'shippingAddress',
        ]

    def get_taxPrice(self, obj):
        fees = OrderFees.objects.first()
        if not fees:
            fees = OrderFees.objects.create()

        items_total = sum(
            Decimal(item.final_price) * item.qty for item in obj.orderItems.all()
        )
        return round(items_total * Decimal(fees.taxRate), 2)

    def get_shippingPrice(self, obj):
        fees = OrderFees.objects.first()
        if not fees:
            fees = OrderFees.objects.create()
        return round(Decimal(fees.shippingPrice), 2)
    
    def get_formatted_created_at(self, obj):
        return obj.createdAt.strftime("%B %d, %Y %I:%M %p")