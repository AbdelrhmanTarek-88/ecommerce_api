from rest_framework.decorators import api_view, permission_classes
from django.views.decorators.cache import cache_page
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from .models import Product, Review, Brand, Category
from .serializers import ProductSerializer, BrandSerializer, CategorySerializer

# Products endpoints
@api_view(['GET'])
@cache_page(60 * 2)
def getProducts(request):
    keyword = request.query_params.get('keyword', '')
    category = request.query_params.get('category', '')
    min_price = request.query_params.get('min_price')
    max_price = request.query_params.get('max_price')
    sort = request.query_params.get('sort', '')

    try:
        if min_price is not None:
            min_price = float(min_price)
            if min_price < 0:
                return Response({'detail': 'Minimum price cannot be negative'}, status=status.HTTP_400_BAD_REQUEST)
        if max_price is not None:
            max_price = float(max_price)
            if max_price < 0:
                return Response({'detail': 'Maximum price cannot be negative'}, status=status.HTTP_400_BAD_REQUEST)
        if min_price is not None and max_price is not None and min_price > max_price:
            return Response({'detail': 'Minimum price cannot be greater than maximum price'}, status=status.HTTP_400_BAD_REQUEST)
    except (ValueError, TypeError):
        return Response({'detail': 'Invalid price format'}, status=status.HTTP_400_BAD_REQUEST)

    valid_sorts = ['price_asc', 'price_desc', '']
    if sort not in valid_sorts:
        return Response({'detail': f'Invalid sort value. Must be one of {valid_sorts}'}, status=status.HTTP_400_BAD_REQUEST)

    products = Product.objects.select_related('user', 'brand', 'category').filter(name__icontains=keyword)

    if category:
        try:
            category_obj = Category.objects.get(id=category)
            products = products.filter(category=category_obj)
        except Category.DoesNotExist:
            return Response({'detail': 'Invalid category ID'}, status=status.HTTP_400_BAD_REQUEST)

    if min_price is not None:
        products = products.filter(price__gte=min_price)
    if max_price is not None:
        products = products.filter(price__lte=max_price)

    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    else:
        products = products.order_by('-created_at')

    paginator = PageNumberPagination()
    paginated_products = paginator.paginate_queryset(products, request)
    serializer = ProductSerializer(paginated_products, many=True)
    return paginator.get_paginated_response(serializer.data)

@api_view(['GET'])
def getProduct(request, pk):
    try:
        product = Product.objects.select_related('user', 'brand', 'category').get(id=pk)
        serializer = ProductSerializer(product, many=False)
        return Response(serializer.data)
    except Product.DoesNotExist:
        return Response({'detail': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)


def get_or_create_brand(brand_input):
    if not brand_input:
        return Brand.objects.get_or_create(name='Unknown Brand')[0]
    try:
        return Brand.objects.get(id=brand_input)
    except (Brand.DoesNotExist, ValueError):
        return Brand.objects.get_or_create(name=str(brand_input))[0]

def get_or_create_category(category_input):
    if not category_input:
        return Category.objects.get_or_create(name='Unknown Category')[0]
    try:
        return Category.objects.get(id=category_input)
    except (Category.DoesNotExist, ValueError):
        return Category.objects.get_or_create(name=str(category_input))[0]

@api_view(['POST'])
@permission_classes([IsAdminUser])
def createProduct(request):
    data = request.data.copy()

    try:
        brand = get_or_create_brand(data.get('brand'))
        category = get_or_create_category(data.get('category'))

        price = float(data.get('price', 0))
        stock = int(data.get('stock', 0))

        if price < 0 or stock < 0:
            return Response({'detail': 'Price or stock cannot be negative'}, status=status.HTTP_400_BAD_REQUEST)

        data['brand'] = brand.id
        data['category'] = category.id

    except (ValueError, TypeError):
        return Response({'detail': 'Invalid input format'}, status=status.HTTP_400_BAD_REQUEST)

    serializer = ProductSerializer(data=data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([IsAdminUser])
def updateProduct(request, pk):
    try:
        product = Product.objects.get(id=pk)
    except Product.DoesNotExist:
        return Response({'detail': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

    data = request.data.copy()

    if 'brand' in data:
        try:
            brand = get_or_create_brand(data['brand'])
            data['brand'] = brand.id
        except:
            return Response({'detail': 'Invalid brand input'}, status=status.HTTP_400_BAD_REQUEST)
    if 'category' in data:
        try:
            category = get_or_create_category(data['category'])
            data['category'] = category.id
        except:
            return Response({'detail': 'Invalid category input'}, status=status.HTTP_400_BAD_REQUEST)

    if 'price' in data:
        try:
            if float(data['price']) < 0:
                return Response({'detail': 'Price cannot be negative'}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'detail': 'Invalid price value'}, status=status.HTTP_400_BAD_REQUEST)

    if 'stock' in data:
        try:
            if int(data['stock']) < 0:
                return Response({'detail': 'Stock cannot be negative'}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'detail': 'Invalid stock value'}, status=status.HTTP_400_BAD_REQUEST)

    serializer = ProductSerializer(product, data=data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def deleteProduct(request, pk):
    try:
        product = Product.objects.get(id=pk)
        product.delete()
        return Response({'detail': 'Product deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    except Product.DoesNotExist:
        return Response({'detail': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def uploadImage(request):
    data = request.data
    if 'product_id' not in data:
        return Response({'detail': 'Product ID is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    product_id = data['product_id']
    try:
        product = Product.objects.get(id=product_id)
        image = request.FILES.get('image')
        if image:
            if not image.content_type.startswith('image/'):
                return Response({'detail': 'Invalid image format'}, status=status.HTTP_400_BAD_REQUEST)
            product.image_field = image
            product.save()
            return Response({'detail': 'Image was uploaded'})
        return Response({'detail': 'No image provided'}, status=status.HTTP_400_BAD_REQUEST)
    except Product.DoesNotExist:
        return Response({'detail': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

# Review endpoints
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


# Brand endpoints
@api_view(['POST'])
@permission_classes([IsAdminUser])
def createBrand(request):
    serializer = BrandSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def getBrands(request):
    brands = Brand.objects.all()
    serializer = BrandSerializer(brands, many=True)
    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([IsAdminUser])
def updateBrand(request, pk):
    try:
        brand = Brand.objects.get(id=pk)
    except Brand.DoesNotExist:
        return Response({'detail': 'Brand not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = BrandSerializer(brand, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def deleteBrand(request, pk):
    try:
        brand = Brand.objects.get(id=pk)
        brand.delete()
        return Response({'detail': 'Brand deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    except Brand.DoesNotExist:
        return Response({'detail': 'Brand not found'}, status=status.HTTP_404_NOT_FOUND)

# Category endpoints 
@api_view(['POST'])
@permission_classes([IsAdminUser])
def createCategory(request):
    serializer = CategorySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def getCategories(request):
    categories = Category.objects.all()
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([IsAdminUser])
def updateCategory(request, pk):
    try:
        category = Category.objects.get(id=pk)
    except Category.DoesNotExist:
        return Response({'detail': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = CategorySerializer(category, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def deleteCategory(request, pk):
    try:
        category = Category.objects.get(id=pk)
        category.delete()
        return Response({'detail': 'Category deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    except Category.DoesNotExist:
        return Response({'detail': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)
