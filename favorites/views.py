from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Favorite
from .serializers import FavoriteSerializer
from products.models import Product

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_favorites(request):
    favorites = Favorite.objects.select_related('product').filter(user=request.user)
    serializer = FavoriteSerializer(favorites, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_favorites(request):
    product_id = request.data.get('product_id')
    if not product_id:
        return Response({'error': 'Product ID is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        product = Product.objects.get(id=product_id)
        favorite, created = Favorite.objects.get_or_create(user=request.user, product=product)
        if not created:
            return Response({'message': 'Already in favorites'}, status=status.HTTP_200_OK)
        return Response({'message': 'Added to favorites'}, status=status.HTTP_201_CREATED)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_from_favorites(request, product_id):
    try:
        favorite = Favorite.objects.get(user=request.user, product_id=product_id)
        favorite.delete()
        return Response({'message': 'Removed from favorites'})
    except Favorite.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def clear_favorites(request):
    deleted_count, _ = Favorite.objects.filter(user=request.user).delete()
    return Response({'message': f'{deleted_count} favorites cleared'})
