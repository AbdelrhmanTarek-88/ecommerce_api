from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import UserProfile
from users.serializers import UserProfileSerializer, UserSerializer
from rest_framework import status

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getUserProfile(request):
    user = request.user
    serializer = UserSerializer(user, many=False)
    return Response(
        serializer.data,
    )

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateUserProfile(request):
    user = request.user
    data = request.data

    user_serializer = UserSerializer(user, data={
        'first_name': data.get('first_name', user.first_name),
        'last_name': data.get('last_name', user.last_name),
    }, partial=True)
    if user_serializer.is_valid(raise_exception=True):
        user = user_serializer.save()

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

    refresh = RefreshToken.for_user(user)
    return Response({
        **UserSerializer(user, many=False).data,
        'token': {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        },
    })

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updatePassword(request):
    user = request.user
    data = request.data

    old_password = data.get('old_password')
    new_password = data.get('new_password')
    confirm_password = data.get('confirm_password')

    if not user.check_password(old_password):
        return Response({'detail': 'Old password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)

    if not new_password:
        return Response({'detail': 'New password cannot be empty.'}, status=status.HTTP_400_BAD_REQUEST)

    if old_password == new_password:
        return Response({'detail': 'New password cannot be the same as the old password.'},status=status.HTTP_400_BAD_REQUEST)

    if new_password != confirm_password:
        return Response({'detail': 'New passwords do not match.'}, status=status.HTTP_400_BAD_REQUEST)

    user.set_password(new_password)
    user.save()

    return Response({'detail': 'Password updated successfully.'})