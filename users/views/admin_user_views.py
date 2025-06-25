from django.contrib.auth.models import User
from users.models import UserProfile
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from users.serializers import UserSerializer, UserProfileSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from core.pagination import CustomPageNumberPagination

@api_view(['GET'])
@permission_classes([IsAdminUser])
def getUsers(request):
    users = User.objects.all().order_by('id')
    paginator = CustomPageNumberPagination()
    page = paginator.paginate_queryset(users, request)
    serializer = UserSerializer(page, many=True)
    return paginator.get_paginated_response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def getUserById(request, pk):
    try:
        user = User.objects.get(id=pk)
        serializer = UserSerializer(user, many=False)
        return Response(serializer.data)
    except User.DoesNotExist:
        return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['PUT'])
@permission_classes([IsAdminUser])
def updateUser(request, pk):
    try:
        user = User.objects.get(id=pk)
        data = request.data

        user.username = data.get('username', user.username)
        user.email = data.get('email', user.email)
        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)
        user.is_staff = data.get('is_staff', user.is_staff)
        user.save()

        try:
            profile = user.profile
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=user)

        profile_data = {
            'phone': data.get('phone', profile.phone),
            'address': data.get('address', profile.address),
            'city': data.get('city', profile.city),
            'postal_code': data.get('postal_code', profile.postal_code),
            'country': data.get('country', profile.country),
        }

        profile_serializer = UserProfileSerializer(profile, data=profile_data, partial=True)
        if profile_serializer.is_valid(raise_exception=True):
            profile_serializer.save()

        serializer = UserSerializer(user, many=False)
        refresh = RefreshToken.for_user(user)

        return Response({
            **serializer.data,
            'token': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            },
        })

    except User.DoesNotExist:
        return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def deleteUser(request, pk):
    try:
        user = User.objects.get(id=pk)
        user.delete()
        return Response({'detail': 'User was deleted'}, status=status.HTTP_204_NO_CONTENT)
    except User.DoesNotExist:
        return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)