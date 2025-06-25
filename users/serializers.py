from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['phone', 'address', 'city', 'postal_code', 'country', 'created_at', 'updated_at']

class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField(read_only=True)
    id = serializers.SerializerMethodField(read_only=True)
    is_staff = serializers.SerializerMethodField(read_only=True)
    profile = UserProfileSerializer(read_only=True)
    favorites_count = serializers.SerializerMethodField(read_only=True)
    cart_items_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'full_name', 'profile', 'is_staff',
            'favorites_count', 'cart_items_count'
        ]

    def get_id(self, obj):
        return obj.id

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    def get_is_staff(self, obj):
        return obj.is_staff

    def get_favorites_count(self, obj):
        return obj.favorites.count() if hasattr(obj, 'favorites') else 0

    def get_cart_items_count(self, obj):
        return obj.cart_items.count() if hasattr(obj, 'cart_items') else 0
    
    def validate_email(self, value):
        user = self.instance
        if user and User.objects.filter(email__iexact=value).exclude(id=user.id).exists():
            raise serializers.ValidationError("Email already exists.")
        return value

    def validate_username(self, value):
        user = self.instance
        if user and User.objects.filter(username__iexact=value).exclude(id=user.id).exists():
            raise serializers.ValidationError("Username already exists.")
        return value

class UserPublicSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['username', 'email', 'full_name', 'phone']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    def get_phone(self, obj):
        return obj.profile.phone if hasattr(obj, 'profile') else None
