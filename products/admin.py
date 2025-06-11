from django.utils.html import format_html
from django.contrib import admin
from .models import Product, Review, Brand, Category

class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0
    readonly_fields = ['user', 'rating', 'comment', 'created_at']

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'price', 'stock', 'created_at', 'category', 'brand', 'average_rating', 'num_reviews', 'source_server', 'image_preview']
    readonly_fields = ['image_preview']
    list_filter = ['category', 'brand', 'stock']
    search_fields = ['name', 'description']
    fieldsets = (
    ('Basic Info', {
        'fields': ('name', 'brand', 'category', 'price', 'stock', 'description')
    }),
    ('Media', {
        'fields': ('image_field', 'image_url', 'image_preview')
    }),
    ('Meta', {
        'fields': ('external_id', 'source_server', 'slug')
    }),
    )
    
    inlines = [ReviewInline]


    def image_preview(self, obj):
        if obj.image_field:
            return format_html('<img src="{}" width="100" height="100" style="border-radius:8px;" />', obj.image_field.url)
        elif obj.image_url:
            return format_html('<img src="{}" width="100" height="100" style="border-radius:8px;" />', obj.image_url)
        return "No Image"

    image_preview.short_description = "Image Preview"



@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'user', 'rating', 'comment', 'created_at']
    list_filter = ['rating']
    search_fields = ['product__name', 'user__username']

    def short_comment(self, obj):
        return (obj.comment[:50] + '...') if obj.comment else ''
    short_comment.short_description = "Comment"

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']