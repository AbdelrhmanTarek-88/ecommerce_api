from django.contrib import admin
from .models import Favorite

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'added_at')
    list_filter = ['added_at']
    search_fields = ('user__username', 'product__name')
    ordering = ('-added_at',)
    list_per_page = 25
