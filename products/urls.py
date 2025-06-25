from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Prodcuts Endpoints
    path('', views.getProducts, name='products'),
    path('create/', views.createProduct, name='create-product'),
    path('upload/', views.uploadImage, name='product-image-upload'),
    path('<int:pk>/update/', views.updateProduct, name='product-update'),
    path('<int:pk>/delete/', views.deleteProduct, name='delete-product'),
    
    # Reviews Endpoints
    path('<int:pk>/reviews/', views.createProductReview, name='product-review'),
    
    # Brand Endpoints
    path('brands/', views.getBrands, name='brands'),
    path('brands/create/', views.createBrand, name='create-brand'),
    path('brands/<int:pk>/update/', views.updateBrand, name='update-brand'),
    path('brands/<int:pk>/delete/', views.deleteBrand, name='delete-brand'),

    # Categories Endpoints
    path('categories/', views.getCategories, name='categories'),
    path('categories/create/', views.createCategory, name='create-category'),
    path('categories/<int:pk>/update/', views.updateCategory, name='update-category'),
    path('categories/<int:pk>/delete/', views.deleteCategory, name='delete-category'),
    
    # Get Product By Slug Or Id 
    path('<str:pk>/', views.getProduct, name='product'),
]