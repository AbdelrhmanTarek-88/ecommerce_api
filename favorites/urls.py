from django.urls import path
from . import views

app_name = 'favorites'

urlpatterns = [
    path('', views.get_favorites, name='get-favorites'),
    path('add/', views.add_to_favorites, name='add-to-favorites'),
    path('<int:product_id>/remove/', views.remove_from_favorites, name='remove-from-favorites'),
    path('clear/', views.clear_favorites, name='clear-favorites'),
]
