from rest_framework.decorators import api_view, permission_classes
from django.views.decorators.cache import cache_page
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from products.models import Product, Brand, Category
from products.serializers import ProductSerializer
from core.pagination import CustomPageNumberPagination, CustomLimitOffsetPagination
from django.db.models import Case, When, Value, BooleanField
from django.utils import timezone
from datetime import timedelta

@api_view(['GET'])
@cache_page(30)
def getProducts(request):
    # Query Params
    keyword = request.query_params.get('keyword', '')
    tag = request.query_params.get('tag')
    category_param = request.query_params.get('category')
    min_price = request.query_params.get('min_price')
    max_price = request.query_params.get('max_price')
    sort = request.query_params.get('sort', '')
    is_discount_active = request.query_params.get("discount_limited") == "true"
    is_new_arrival = request.query_params.get("new") == "true"
    is_popular = request.query_params.get("popular") == "true"
    min_discount = request.query_params.get("min_discount")
    max_discount = request.query_params.get("max_discount")

    # --- Validate numeric filters ---
    try:
        min_price = float(min_price) if min_price is not None else None
        max_price = float(max_price) if max_price is not None else None
        min_discount = int(min_discount) if min_discount is not None else None
        max_discount = int(max_discount) if max_discount is not None else None

        if min_price is not None and min_price < 0:
            return Response({"detail": "Minimum price cannot be negative."}, status=400)
        if max_price is not None and max_price < 0:
            return Response({"detail": "Maximum price cannot be negative."}, status=400)
        if min_price is not None and max_price is not None and min_price > max_price:
            return Response({"detail": "Minimum price cannot be greater than maximum price."}, status=400)

        if min_discount is not None and (min_discount < 0 or min_discount > 100):
            return Response({"detail": "Minimum discount must be between 0 and 100."}, status=400)
        if max_discount is not None and (max_discount < 0 or max_discount > 100):
            return Response({"detail": "Maximum discount must be between 0 and 100."}, status=400)
        if min_discount is not None and max_discount is not None and min_discount > max_discount:
            return Response({"detail": "Minimum discount cannot be greater than maximum discount."}, status=400)

    except (ValueError, TypeError):
        return Response({"detail": "Invalid numeric input."}, status=400)


    # Validate sort
    sort_map = {
        'price_asc': 'price',
        'price_desc': '-price',
        'rating_desc': '-average_rating',
        '': '-created_at',
    }
    sort = request.query_params.get('sort', '').strip()
    if sort not in sort_map:
        return Response({
            'detail': f'Invalid sort value. Allowed values are: {", ".join([k or "default" for k in sort_map.keys()])}'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Build queryset
    products = Product.objects.select_related('user', 'brand', 'category').filter(is_published=True)

    # Annotate properties as real DB fields
    products = products.annotate(
    has_active_discount=Case(
        When(
            discount__gt=0,
            discount_start__lte=timezone.now(),
            discount_end__gte=timezone.now(),
            then=Value(True)
        ),
        default=Value(False),
        output_field=BooleanField()
    ),
    is_recent_arrival=Case(
        When(
            published_at__gte=timezone.now() - timedelta(days=7),
            then=Value(True)
        ),
        default=Value(False),
        output_field=BooleanField()
    )
)
    if is_discount_active:
        products = products.filter(has_active_discount=True)

    if is_new_arrival:
        products = products.filter(is_recent_arrival=True)
    
    if is_popular:
        products = products.filter(is_popular=True)

    if keyword:
        products = products.filter(name__icontains=keyword)

    if tag:
        products = products.filter(tags__name__icontains=tag)


    if category_param:
        try:
            category_obj = Category.objects.get(id=category_param) if category_param.isdigit() else Category.objects.get(slug=category_param)
            products = products.filter(category=category_obj)
        except Category.DoesNotExist:
            return Response({'detail': 'Invalid category'}, status=status.HTTP_400_BAD_REQUEST)

    if min_price is not None:
        products = products.filter(price__gte=min_price)
    if max_price is not None:
        products = products.filter(price__lte=max_price)   

    if min_discount is not None:
        products = products.filter(discount__gte=min_discount)
    if max_discount is not None:
        products = products.filter(discount__lte=max_discount)
    
    products = products.order_by(sort_map[sort])

    # Pagination
    if 'limit' in request.query_params or 'offset' in request.query_params:
        paginator = CustomLimitOffsetPagination()
    else:
        paginator = CustomPageNumberPagination()

    paginated_products = paginator.paginate_queryset(products, request)

    serializer = ProductSerializer(paginated_products, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
def getProduct(request, pk):
    try:
        if pk.isdigit():
            product = Product.objects.select_related('user', 'brand', 'category').get(id=pk)
        else:
            product = Product.objects.select_related('user', 'brand', 'category').get(slug=pk)
        
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
        name = str(brand_input).strip().title() if brand_input else 'Unknown Brand'
        return Brand.objects.get_or_create(name=name)[0]

def get_or_create_category(category_input):
    if not category_input:
        return Category.objects.get_or_create(name='Unknown Category')[0]
    try:
        return Category.objects.get(id=category_input)
    except (Category.DoesNotExist, ValueError):
        name = str(category_input).strip().title() if category_input else 'Unknown Category'
        return Category.objects.get_or_create(name=name)[0]

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

        if 'tags' in data and not isinstance(data['tags'], list):
            return Response({'detail': 'Tags must be a list of strings'}, status=status.HTTP_400_BAD_REQUEST)

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
        
    if 'tags' in data and not isinstance(data['tags'], list):
        return Response({'detail': 'Tags must be a list of strings'}, status=status.HTTP_400_BAD_REQUEST)

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
@permission_classes([IsAdminUser])
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
            
            if product.image_field:
                product.image_field.delete(save=False)
            
            product.image_field = image
            product.save()
            image_url = request.build_absolute_uri(product.image_field.url)
            return Response({
                'detail': 'Image was uploaded',
                'image_url': image_url
            })
        return Response({'detail': 'No image provided'}, status=status.HTTP_400_BAD_REQUEST)
    except Product.DoesNotExist:
        return Response({'detail': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
