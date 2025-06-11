from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination

from cart_item.models import CartItem
from .models import Order, OrderItem, ShippingAddress, OrderFees
from .serializers import OrderSerializer
from products.models import Product
from django.utils.timezone import now
from django.db import transaction


class OrderPagination(PageNumberPagination):
    page_size = 10

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getOrderFees(request):
    fees = OrderFees.objects.first()
    if not fees:
        fees = OrderFees.objects.create()
    return Response({
        'taxRate': fees.taxRate,
        'shippingPrice': fees.shippingPrice,
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def addOrderItems(request):
    user = request.user
    data = request.data

    orderItems = data.get('orderItems')
    if not orderItems or not isinstance(orderItems, list) or len(orderItems) == 0:
        return Response({'detail': 'No order items'}, status=status.HTTP_400_BAD_REQUEST)

    required_fields = ['paymentMethod', 'shippingAddress']
    for field in required_fields:
        if not data.get(field):
            return Response({'detail': f'Missing or empty field: {field}'}, status=status.HTTP_400_BAD_REQUEST)

    shippingAddress = data.get('shippingAddress', {})
    required_address_fields = ['address', 'city', 'postalCode', 'country']
    for field in required_address_fields:
        if not shippingAddress.get(field):
            return Response({'detail': f'Missing shipping address field: {field}'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        with transaction.atomic():
            fees = OrderFees.objects.first() or OrderFees.objects.create()
            items_total = 0
            product_ids = [item['product'] for item in orderItems]
            products = Product.objects.filter(id__in=product_ids).in_bulk()

            seen_products = set()
            for item in orderItems:
                product_id = int(item['product'])
                if product_id in seen_products:
                    return Response(
                        {'detail': f'Duplicate product found in order items: {product_id}'},status=status.HTTP_400_BAD_REQUEST)
                seen_products.add(product_id)
                product = products.get(product_id)
                if not product:
                    return Response({'detail': f'Product with ID {product_id} not found'}, status=status.HTTP_404_NOT_FOUND)

                qty = int(item['qty'])
                if qty <= 0:
                    return Response({'detail': 'Quantity must be greater than 0'}, status=status.HTTP_400_BAD_REQUEST)

                if qty > product.stock:
                    return Response({'detail': f'Not enough stock for {product.name}'}, status=status.HTTP_400_BAD_REQUEST)

                price = float(item['price'])
                if price != float(product.price):
                    return Response({'detail': f'Price mismatch for {product.name}'}, status=status.HTTP_400_BAD_REQUEST)

                items_total += price * qty

            taxPrice = items_total * float(fees.taxRate)
            shippingPrice = float(fees.shippingPrice)
            calculated_total = items_total + taxPrice + shippingPrice

            order = Order.objects.create(
                user=user,
                paymentMethod=data['paymentMethod'],
                totalPrice=calculated_total
            )

            ShippingAddress.objects.create(
                order=order,
                address=shippingAddress.get('address'),
                city=shippingAddress.get('city'),
                postalCode=shippingAddress.get('postalCode'),
                country=shippingAddress.get('country'),
                phone=shippingAddress.get('phone'),
            )

            for item in orderItems:
                product = products[int(item['product'])]
                qty = int(item['qty'])

                OrderItem.objects.create(
                    product=product,
                    order=order,
                    name=product.name,
                    qty=qty,
                    price=product.price,
                )

                product.stock -= qty
                product.save()
                
            CartItem.objects.filter(user=user).delete()
            serializer = OrderSerializer(order, many=False, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({'detail': 'Failed to create order', 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getOrderById(request, pk):
    user = request.user
    try:
        order = Order.objects.get(id=pk)
        if user.is_staff or order.user == user:
            serializer = OrderSerializer(order, many=False, context={'request': request})
            return Response(serializer.data)
        return Response({'detail': 'Not authorized to view this order'}, status=status.HTTP_403_FORBIDDEN)
    except Order.DoesNotExist:
        return Response({'detail': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT'])
@permission_classes([IsAdminUser])
def updateOrderToPaid(request, pk):
    user = request.user
    try:
        order = Order.objects.get(id=pk)
        if user.is_staff or order.user == user:
            order.isPaid = True
            order.paidAt = now()
            order.status = 'shipped'
            order.save()
            return Response({'detail': 'Order payment updated successfully'})
        return Response({'detail': 'Not authorized to update this order'}, status=status.HTTP_403_FORBIDDEN)
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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getMyOrders(request):
    user = request.user
    orders = Order.objects.filter(user=user).select_related('user').prefetch_related('orderItems', 'shippingAddress')
    paginator = OrderPagination()
    paginated_orders = paginator.paginate_queryset(orders, request)
    serializer = OrderSerializer(paginated_orders, many=True, context={'request': request})
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def getAllOrders(request):
    orders = Order.objects.all().select_related('user').prefetch_related('orderItems', 'shippingAddress')
    paginator = OrderPagination()
    paginated_orders = paginator.paginate_queryset(orders, request)
    serializer = OrderSerializer(paginated_orders, many=True, context={'request': request})
    return paginator.get_paginated_response(serializer.data)
