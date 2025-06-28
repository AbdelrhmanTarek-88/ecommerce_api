from rest_framework import serializers
from .models import Product, Review, Brand, Category
from taggit.serializers import TagListSerializerField, TaggitSerializer

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
        fields = ['id', 'name', 'slug']
        read_only_fields = ['slug']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']
        read_only_fields = ['slug']

class ProductSerializer(serializers.ModelSerializer, TaggitSerializer):
    image = serializers.SerializerMethodField()
    image_field = serializers.ImageField(write_only=True, required=False)
    image_url = serializers.URLField(write_only=True, required=False)
    brand = serializers.PrimaryKeyRelatedField(queryset=Brand.objects.all(), write_only=True,)
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), write_only=True)
    brand_name = serializers.StringRelatedField(source='brand', read_only=True)
    category_name = serializers.StringRelatedField(source='category', read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    tags = TagListSerializerField()
    final_price = serializers.DecimalField( max_digits=10, decimal_places=2, read_only=True)
    is_published = serializers.BooleanField(required=False, write_only=True)
    published_at = serializers.DateTimeField(required=False, write_only=True)
    is_new_arrival = serializers.SerializerMethodField()
    is_visible = serializers.SerializerMethodField()
    is_discount_active = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
                'id', 'name', 'slug', 'brand', 'brand_name', 'category', 'category_name', 'model', 'color','is_new_arrival', 'is_popular', 
                'description', 'num_reviews', 'average_rating', 'price', 'discount', 'is_discount_active', 'discount_start', 'discount_end', 'final_price','stock',
                'image','image_field', 'image_url', 'created_at', 'reviews', 'tags', 'is_published', 'published_at', 'is_visible',
            ]
        
        read_only_fields = ['slug', 'final_price','created_at', 'average_rating', 'num_reviews']

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image_field:
            try:
                return request.build_absolute_uri(obj.image_field.url)
            except:
                return None
        return obj.image_url

    def is_new_arrival(self, obj):
        return obj.is_new_arrival

    def get_is_visible(self, obj):
        return obj.is_visible

    def get_is_discount_active(self, obj):
        return obj.is_discount_active