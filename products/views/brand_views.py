from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from products.models import Brand
from products.serializers import BrandSerializer
from core.pagination import CustomPageNumberPagination

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
    paginator = CustomPageNumberPagination()
    page = paginator.paginate_queryset(brands, request)
    serializer = BrandSerializer(page, many=True)
    return paginator.get_paginated_response(serializer.data)

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