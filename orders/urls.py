from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # Admin Routes
    path('', views.getAllOrders, name='all-orders'),
    path('fees/', views.getOrderFees, name='order-fees'),

    # Authenticated User Routes
    path('add/', views.addOrderItems, name='add-order'),
    path('myorders/', views.getMyOrders, name='my-orders'), 

    # Order Actions
    path('<str:pk>/', views.getOrderById, name='order-detail'),
    path('<str:pk>/pay/', views.updateOrderToPaid, name='pay'),  
    path('<str:pk>/deliver/', views.updateOrderToDelivered, name='deliver'),

]