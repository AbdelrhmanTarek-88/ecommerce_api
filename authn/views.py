from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

@api_view(['POST'])
@permission_classes([AllowAny])
@swagger_auto_schema(
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['first_name', 'last_name', 'username', 'email', 'password', 'confirm_password'],
        properties={
            'first_name': openapi.Schema(type=openapi.TYPE_STRING, description='First name of the user'),
            'last_name': openapi.Schema(type=openapi.TYPE_STRING, description='Last name of the user'),
            'username': openapi.Schema(type=openapi.TYPE_STRING, description='Unique username'),
            'email': openapi.Schema(type=openapi.TYPE_STRING, description='Unique email address'),
            'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password', format='password'),
            'confirm_password': openapi.Schema(type=openapi.TYPE_STRING, description='Confirm password', format='password'),
        },
    ),
    responses={
        201: openapi.Response(
            description="User registered successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'full_name': openapi.Schema(type=openapi.TYPE_STRING),
                    'username': openapi.Schema(type=openapi.TYPE_STRING),
                    'email': openapi.Schema(type=openapi.TYPE_STRING),
                    'token': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'refresh': openapi.Schema(type=openapi.TYPE_STRING),
                            'access': openapi.Schema(type=openapi.TYPE_STRING),
                        }
                    ),
                }
            )
        ),
        400: "Bad Request - Validation Error"
    }
)
def registerUser(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'full_name': f"{user.first_name} {user.last_name}",
            'username': user.username,
            'email': user.email,
            'token': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logoutUser(request):
    try:
        refresh_token = request.data.get('refresh')
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({'detail': 'Successfully logged out'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
