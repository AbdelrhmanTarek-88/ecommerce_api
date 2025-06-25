from django.db import models
from django.contrib.auth.models import User
from products.models import Product
from django.core.validators import MinValueValidator
from decimal import Decimal

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    paymentMethod = models.CharField(max_length=200, null=True, blank=True, default="Cash")
    totalPrice = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=Decimal('0.00'))
    isPaid = models.BooleanField(default=False)
    paidAt = models.DateTimeField(null=True, blank=True)
    isDelivered = models.BooleanField(default=False)
    deliveredAt = models.DateTimeField(null=True, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Order {self.id} by {self.user.username if self.user else 'Guest'}"

    class Meta:
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['createdAt']),
        ]


class ShippingAddress(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='shippingAddress')
    address = models.CharField(max_length=200, null=True, blank=True)
    postalCode = models.CharField(max_length=20, null=True, blank=True)
    city = models.CharField(max_length=200, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.address or "No address provided"


class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='orderItems')
    name = models.CharField(max_length=200, null=True, blank=True)
    qty = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    original_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    discount = models.PositiveIntegerField(null=True, blank=True)
    final_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.qty} x {self.name or 'Unnamed'} (Order #{self.order.id})"

    def save(self, *args, **kwargs):
        if self.product and (not self.name or self.name.strip() == ""):
            self.name = self.product.name
            self.original_price = self.product.price
            self.discount = self.product.discount or 0
            self.final_price = self.product.final_price
            self.total = (self.final_price * self.qty).quantize(Decimal('0.01'))
        super().save(*args, **kwargs)


class OrderFees(models.Model):
    taxRate = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0.05, 
        validators=[MinValueValidator(Decimal('0.00'))], 
        help_text="Tax rate as a percentage (e.g., 0.05 for 5%)"
    )
    shippingPrice = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=10.00, 
        validators=[MinValueValidator(Decimal('0.00'))], 
        help_text="Fixed shipping price"
    )
    updatedAt = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Order Fees"
        verbose_name_plural = "Order Fees"

    def save(self, *args, **kwargs):
        self.__class__.objects.exclude(id=self.id).delete()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Tax: {self.taxRate}%, Shipping: {self.shippingPrice}"