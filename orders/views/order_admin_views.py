from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from orders.models import Order
from orders.serializers import OrderSerializer
from django.utils.timezone import now
from core.pagination import CustomPageNumberPagination

@api_view(['GET'])
@permission_classes([IsAdminUser])
def getAllOrders(request):
    orders = Order.objects.all().select_related('user').prefetch_related('orderItems', 'shippingAddress').order_by('id')
    paginator = CustomPageNumberPagination()
    paginated_orders = paginator.paginate_queryset(orders, request)
    serializer = OrderSerializer(paginated_orders, many=True, context={'request': request})
    return paginator.get_paginated_response(serializer.data)

@api_view(['PUT'])
@permission_classes([IsAdminUser])
def updateOrderToPaid(request, pk):
    user = request.user
    try:
        order = Order.objects.get(id=pk)
        order.isPaid = True
        order.paidAt = now()
        order.status = 'shipped'
        order.save()
        return Response({'detail': 'Order payment updated successfully'})
    except Order.DoesNotExist:
        return Response({'detail': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['PUT'])
@permission_classes([IsAdminUser])
def updateOrderToDelivered(request, pk):
    try:
        order = Order.objects.get(id=pk)
        order.isDelivered = True
        order.deliveredAt = now()
        order.status = 'delivered'
        order.save()
        return Response({'detail': 'Order delivery updated successfully'})
    except Order.DoesNotExist:
        return Response({'detail': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
