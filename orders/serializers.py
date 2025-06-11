from rest_framework import serializers
from .models import Order, OrderItem, ShippingAddress, OrderFees
from users.serializers import UserPublicSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'name', 'qty', 'price', 'image']

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.product and obj.product.image_url and request:
            return request.build_absolute_uri(obj.product.image_url)
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
        items_total = sum(float(item.price) * item.qty for item in obj.orderItems.all())
        return items_total * float(fees.taxRate)

    def get_shippingPrice(self, obj):
        fees = OrderFees.objects.first()
        if not fees:
            fees = OrderFees.objects.create()
        return float(fees.shippingPrice)
    
    def get_formatted_created_at(self, obj):
        return obj.createdAt.strftime("%B %d, %Y %I:%M %p")