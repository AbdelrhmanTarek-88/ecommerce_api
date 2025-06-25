from django.contrib import admin
from .models import Product, Review, Brand, Category
from django.utils.html import format_html



@admin.action(description="Mark selected products as Published")
def make_published(modeladmin, request, queryset):
    queryset.update(is_published=True)

@admin.action(description="UnMark selected products as published")
def make_unpublished(modeladmin, request, queryset):
    queryset.update(is_published=False)

@admin.action(description="Mark selected products as On Sale")
def mark_on_sale(modeladmin, request, queryset):
    queryset.update(is_on_sale=True)

@admin.action(description="Unmark selected products as On Sale")
def unmark_on_sale(modeladmin, request, queryset):
    queryset.update(is_on_sale=False)

@admin.action(description="Mark selected products as Popular")
def mark_popular(modeladmin, request, queryset):
    queryset.update(is_popular=True)

@admin.action(description="Unmark selected products as Popular")
def unmark_popular(modeladmin, request, queryset):
    queryset.update(is_popular=False)

@admin.action(description="Mark selected products as New Arrival")
def mark_new_arrival(modeladmin, request, queryset):
    queryset.update(is_new_arrival=True)

@admin.action(description="Unmark selected products as New Arrival")
def unmark_new_arrival(modeladmin, request, queryset):
    queryset.update(is_new_arrival=False)


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
    
    def classification(self, obj):
        badges = []
        if obj.is_new_arrival:
            badges.append('<div style="background-color:#e0f7fa; text-align:center; color:#00796b; padding:2px 6px; border-radius:8px; margin-bottom:4px;">New</div>')
        if obj.is_popular:
            badges.append('<div style="background-color:#fff3e0; text-align:center; color:#e65100; padding:2px 6px; border-radius:8px; margin-bottom:4px;">Popular</div>')
        if obj.is_on_sale:
            badges.append('<div style="background-color:#ffebee; text-align:center; color:#c62828; padding:2px 6px; border-radius:8px; margin-bottom:4px;">On Sale</div>')
        if not badges:
            return
        return format_html("".join(badges))
    classification.short_description = "Classification"

    list_display = ['id', 'name', 'price', 'stock','is_visible', 'classification', 'created_at', 'category', 'brand', 'average_rating', 'num_reviews', 'source_server', 'image_preview']
    readonly_fields = ['final_price','image_preview', 'created_at','updated_at']
    list_filter = ['created_at','updated_at','source_server', 'category', 'brand',]
    search_fields = ['name', 'description']

    actions = [
    make_published, make_unpublished,
    mark_new_arrival, unmark_new_arrival,
    mark_popular, unmark_popular,
    mark_on_sale, unmark_on_sale,
]


    fieldsets = (
        ('Product Info', {
            'fields': (
                'name', 'brand', 'category', 'model', 'color',
                'price', 'discount', 'final_price', 'stock'
            )
        }),
        ('Classification & Tags', {
            'fields': (
                'is_new_arrival', 'is_popular', 'is_on_sale', 'tags'
            )
        }),
        ('Media', {
            'fields': (
                'image_field', 'image_url', 'image_preview'
            )
        }),
        ('Publishing', {
            'fields': (
                'is_published', 'published_at'
            )
        }),
        ('Metadata', {
            'fields': (
                'description', 'external_id', 'source_server', 'slug',
                'created_at', 'updated_at'
            )
        }),
    )

    inlines = [ReviewInline]

    def final_price(self, obj):
        return obj.final_price
    final_price.short_description = 'Final Price'

    def is_visible(self, obj):
        return obj.is_visible
    is_visible.short_description = "Visible"
    is_visible.boolean = True

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
    list_display = ['id', 'name', 'created_at']
    search_fields = ['name']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'created_at']
    search_fields = ['name']


