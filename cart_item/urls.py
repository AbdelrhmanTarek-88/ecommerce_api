from django.urls import path
from . import views

app_name = 'cart_item'

urlpatterns = [
    path('', views.get_cart_items, name='get-cart-items'),
    path('add/', views.add_to_cart, name='add-to-cart'),
    path('add-from-favorites/', views.add_all_favorites_to_cart, name='add-from-favorites'),
    path('update/<int:product_id>/', views.update_cart_item, name='update-cart-item'),
    path('remove/<int:product_id>/', views.remove_from_cart, name='remove-from-cart'),
    path('clear/', views.clear_cart, name='clear-cart'),
]
