from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import CartItem
from .serializers import CartItemSerializer
from products.models import Product
from favorites.models import Favorite

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_cart_items(request):
    cart_items = CartItem.objects.filter(user=request.user)
    serializer = CartItemSerializer(cart_items, many=True)

    total = sum(item.quantity * item.product.final_price for item in cart_items)

    return Response({
        'cart_items': serializer.data,
        'total': round(total, 2)
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_cart(request):
    product_id = request.data.get('product_id')
    quantity = int(request.data.get('quantity', 1))
    try:
        product = Product.objects.get(id=product_id)
        if product.stock == 0:
            return Response({'error': 'Product is out of stock'}, status=status.HTTP_400_BAD_REQUEST)
        cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
        new_quantity = quantity if created else cart_item.quantity + quantity
        if new_quantity > product.stock:
            return Response(
                {'error': f'Only {product.stock} item(s) in stock'},
                status=status.HTTP_400_BAD_REQUEST
            )
        cart_item.quantity = new_quantity
        cart_item.save()
        return Response({'message': 'Product added to cart'})
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_all_favorites_to_cart(request):
    favorites = Favorite.objects.select_related('product').filter(user=request.user)
    added = 0
    skipped = []
    for fav in favorites:
        product = fav.product
        if product.stock == 0:
            skipped.append({'product_id': product.id, 'reason': 'Out of stock'})
            continue
        cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
        new_quantity = 1 if created else cart_item.quantity + 1
        if new_quantity > product.stock:
            skipped.append({'product_id': product.id, 'reason': f'Only {product.stock} in stock'})
            continue
        cart_item.quantity = new_quantity
        cart_item.save()
        added += 1
    return Response({
        'message': f'{added} item(s) added to cart from favorites.',
        'skipped': skipped
    }, status=status.HTTP_200_OK)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_cart_item(request, product_id):
    quantity = int(request.data.get('quantity', 1))
    try:
        cart_item = CartItem.objects.get(user=request.user, product_id=product_id)
        if quantity > cart_item.product.stock:
            return Response({'error': f'Not enough stock, Only {cart_item.product.stock} item(s)'}, status=status.HTTP_400_BAD_REQUEST)
        cart_item.quantity = quantity
        cart_item.save()
        return Response({'message': 'Cart item updated'})
    except CartItem.DoesNotExist:
        return Response({'error': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_from_cart(request, product_id):
    cart_item = CartItem.objects.filter(user=request.user, product_id=product_id).first()
    if cart_item:
        cart_item.delete()
        return Response({'message': 'Product removed from cart'})
    return Response({'error': 'Item not found in cart'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def clear_cart(request):
    CartItem.objects.filter(user=request.user).delete()
    return Response({'message': 'Cart cleared successfully'})
