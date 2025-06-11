from rest_framework import serializers
from .models import Product, Review, Brand, Category

class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ['user', 'rating', 'comment', 'created_at']

    def get_user(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'name']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class ProductSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    image_field = serializers.ImageField(write_only=True, required=False)
    image_url = serializers.URLField(write_only=True, required=False)
    brand = serializers.PrimaryKeyRelatedField(queryset=Brand.objects.all(), write_only=True,)
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), write_only=True)
    brand_name = serializers.StringRelatedField(source='brand', read_only=True)
    category_name = serializers.StringRelatedField(source='category', read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'brand', 'brand_name', 'category', 'category_name',
            'description', 'num_reviews', 'average_rating', 'price', 'stock',
            'image','image_field', 'image_url', 'slug', 'created_at', 'reviews'
        ]
        read_only_fields = ['image']

    def get_image(self, obj):
        if obj.image_field:
            try:
                return obj.image_field.url
            except:
                return None
        return obj.image_url