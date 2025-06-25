from django.urls import path
from . import views
app_name = 'users'

urlpatterns = [
    # User Profile
    path('profile/', views.getUserProfile, name='user-profile'),
    path('profile/update/', views.updateUserProfile, name='user-profile-update'),
    path('profile/update-password/', views.updatePassword, name='user-profile-update-password'),
    # Admin
    path('', views.getUsers, name='users'),
    path('<str:pk>/', views.getUserById, name='get-user-by-id'),
    path('<str:pk>/update/', views.updateUser, name='update-user'),
    path('<str:pk>/delete/', views.deleteUser, name='delete-user'),

]
