from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import UserProfile
from users.serializers import UserProfileSerializer, UserSerializer

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
        'username': data.get('username', user.username),
        'email': data.get('email', user.email),
        'first_name': data.get('first_name', user.first_name),
        'last_name': data.get('last_name', user.last_name),
    }, partial=True)
    if user_serializer.is_valid(raise_exception=True):
        user = user_serializer.save()

    if 'password' in data and data['password']:
        user.set_password(data['password'])
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

    refresh = RefreshToken.for_user(user)
    return Response({
        **UserSerializer(user, many=False).data,
        'token': {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        },
    })