from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import  IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from products.models import Product, Review

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createProductReview(request, pk):
    user = request.user
    try:
        product = Product.objects.get(id=pk)
    except Product.DoesNotExist:
        return Response({'detail': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
    
    data = request.data
    alreadyExists = product.reviews.filter(user=user).exists()
    if alreadyExists:
        return Response({'detail': 'Product already reviewed'}, status=status.HTTP_400_BAD_REQUEST)

    rating = data.get('rating', 0)
    if not isinstance(rating, int) or rating < 1 or rating > 5:
        return Response({'detail': 'Rating must be an integer between 1 and 5'}, status=status.HTTP_400_BAD_REQUEST)

    comment = data.get('comment', '').strip()
    if not comment:
        return Response({'detail': 'Comment is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    Review.objects.create(
        user=user,
        product=product,
        rating=rating,
        comment=data.get('comment'),
    )

    product.update_reviews()
    return Response({'detail': 'Review added'}, status=status.HTTP_201_CREATED)