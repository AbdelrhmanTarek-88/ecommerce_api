from rest_framework import serializers
from .models import CartItem
from products.models import Product

class CartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source='product.id', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    quantity = serializers.IntegerField()
    product_price = serializers.DecimalField(source='product.price',max_digits=10, decimal_places=2, read_only=True)
    product_discount = serializers.IntegerField(source='product.discount', read_only=True)
    product_final_price = serializers.DecimalField(source='product.final_price',max_digits=10, decimal_places=2, read_only=True)
    product_image = serializers.SerializerMethodField(read_only=True)
    subtotal = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = CartItem
        fields = ['id', 'product_id', 'product_name', 'product_price', 'product_discount', 'product_final_price', 'product_image', 'quantity', 'added_at', 'subtotal']
    
    def get_subtotal(self, obj):
        return round(obj.quantity * obj.product.final_price, 2)
    
    def validate_quantity(self, value):
        product = None

        if self.instance:
            product = self.instance.product
        else:
            product_id = self.initial_data.get('product_id')
            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                raise serializers.ValidationError("Product does not exist")

        if product and value > product.stock:
            raise serializers.ValidationError(f"Not enough stock. Only {product.stock} item(s) available.")
        
        return value

    def get_product_image(self, obj):
        product = obj.product
        request = self.context.get('request')
        
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