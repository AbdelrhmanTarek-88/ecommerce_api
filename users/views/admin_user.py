from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from users.serializers import UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.pagination import PageNumberPagination

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

@api_view(['GET'])
@permission_classes([IsAdminUser])
def getUsers(request):
    users = User.objects.all()
    paginator = StandardResultsSetPagination()
    page = paginator.paginate_queryset(users, request)
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)

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
        user.first_name = data.get('name', user.first_name)
        user.is_staff = data.get('isAdmin', user.is_staff)
        user.save()

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