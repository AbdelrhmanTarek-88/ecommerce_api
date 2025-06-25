from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from orders.models import OrderFees

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
