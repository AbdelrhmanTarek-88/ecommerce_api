from rest_framework import serializers
from .models import Favorite

class FavoriteSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source='product.id', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_image = serializers.SerializerMethodField(read_only=True)
    product_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)
    product_discount = serializers.IntegerField(source='product.discount', read_only=True)
    product_final_price = serializers.DecimalField(source='product.final_price',max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Favorite
        fields = ['id', 'product_id', 'product_name', 'product_image', 'product_price', 'product_discount', 'product_final_price', 'added_at']

    def get_product_image(self, obj):
            if obj.product.image_field:
                try:
                    return obj.product.image_field.url
                except:
                    return None
            return obj.product.image_url


