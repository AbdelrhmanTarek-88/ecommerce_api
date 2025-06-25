from django.db import models
from django.contrib.auth.models import User
from products.models import Product

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='favorited_by')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'product'], name='unique_favorite')
        ]

    def __str__(self):
        return f"{self.user.username} -> {self.product.name}"
