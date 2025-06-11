from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class Brand(models.Model):
    name = models.CharField(max_length=200, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=200, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

class Product(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    external_id = models.CharField(max_length=100, null=True, blank=True)
    source_server = models.CharField(max_length=100, null=True, blank=True, default='Internal Server')
    name = models.CharField(max_length=200, null=True, default='Sample Product')
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(null=True, blank=True, default='')
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=0.00, validators=[MinValueValidator(0.00)])
    stock = models.IntegerField(null=True, default=10)
    image_field = models.ImageField(null=True, blank=True, default='/placeholder.png')
    image_url = models.URLField(max_length=1000, null=True, blank=True, default='')
    slug = models.SlugField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    average_rating = models.FloatField(default=0.0)
    num_reviews = models.IntegerField(default=0)

    class Meta:
        unique_together = ['external_id', 'source_server']

    def __str__(self):
        return f"{self.name} ({self.source_server or 'Manual'})"

    def update_reviews(self):
        reviews = self.reviews.all()
        self.num_reviews = reviews.count()
        self.average_rating = reviews.aggregate(models.Avg('rating'))['rating__avg'] or 0.0
        self.save()

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=False
    )
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['product', 'user']

    def __str__(self):
        return f"{self.rating} by {self.user}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.product.update_reviews()

    def delete(self, *args, **kwargs):
        product = self.product
        super().delete(*args, **kwargs)
        product.update_reviews()
