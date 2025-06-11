from rest_framework import serializers
from .models import CartItem
from products.models import Product

class CartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source='product.id', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    quantity = serializers.IntegerField()
    product_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)
    product_image = serializers.URLField(source='product.image_url', read_only=True)
    subtotal = serializers.SerializerMethodField()
    class Meta:
        model = CartItem
        fields = ['id', 'product_id', 'product_name', 'product_price', 'product_image', 'quantity', 'added_at', 'subtotal']
    
    def get_subtotal(self, obj):
        return round(obj.quantity * obj.product.price, 2)
    
    def validate_quantity(self, value):
        product = self.instance.product if self.instance else self.initial_data.get('product')
        if isinstance(product, Product):
            stock = product.stock
        else:
            product_id = self.initial_data.get('product_id')
            try:
                product = Product.objects.get(id=product_id)
                stock = product.stock
            except Product.DoesNotExist:
                raise serializers.ValidationError("Product does not exist")
        if value > stock:
            raise serializers.ValidationError(f"Not enough stock. Only {stock} item(s) available.")
        return value
    
    