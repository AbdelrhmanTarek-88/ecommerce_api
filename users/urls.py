from django.urls import path
from .views import getUserProfile, updateUserProfile, getUsers, getUserById, updateUser, deleteUser

app_name = 'users'

urlpatterns = [
    path('profile/', getUserProfile, name='user-profile'),
    path('profile/update/', updateUserProfile, name='user-profile-update'),
    path('', getUsers, name='users'),
    path('update/<str:pk>/', updateUser, name='update-user'),
    path('delete/<str:pk>/', deleteUser, name='delete-user'),
    path('<str:pk>/', getUserById, name='get-user-by-id'),

]
