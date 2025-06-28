from django.db import models
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.validators import MinValueValidator, MaxValueValidator
from taggit.managers import TaggableManager
from django.utils.text import slugify
import uuid
from decimal import Decimal, ROUND_HALF_UP
from django.utils import timezone
from datetime import timedelta

class Brand(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name = self.name.strip().title()
        new_slug = slugify(self.name)
        if self.slug != new_slug:
            self.slug = new_slug
        super().save(*args, **kwargs)


class Category(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name = self.name.strip().title()
        new_slug = slugify(self.name)
        if self.slug != new_slug:
            self.slug = new_slug
        super().save(*args, **kwargs)

class Product(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    external_id = models.CharField(max_length=100, null=True, blank=True)
    source_server = models.CharField(max_length=100, null=True, blank=True, default='Internal Server')
    name = models.CharField(max_length=200, null=True, default='Sample Product')
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(null=True, blank=True, default='')
    model	= models.CharField(max_length=200, null=True, blank=True)
    color = models.CharField(max_length=200, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=Decimal('0.00'), validators=[MinValueValidator(Decimal('0.00'))])
    discount = models.PositiveIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Enter discount as a percentage (1 - 100)"
    )
    discount_start = models.DateTimeField(null=True, blank=True)
    discount_end = models.DateTimeField(null=True, blank=True)
    stock = models.IntegerField(null=True, default=10)
    image_field = models.ImageField(null=True, blank=True,)
    image_url = models.URLField(max_length=1000, null=True, blank=True, default='https://cdn.shopify.com/s/files/1/0533/2089/files/placeholder-images-image_large.png')
    average_rating = models.FloatField(default=0.0)
    num_reviews = models.IntegerField(default=0)
    is_popular = models.BooleanField(default=False)
    slug = models.SlugField(max_length=255, blank=True, unique=True)
    tags = TaggableManager(blank=True)
    is_published = models.BooleanField(default=True)
    published_at = models.DateTimeField(null=True, blank=True, default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['external_id', 'source_server']

    def __str__(self):
        return f"{self.name} ({self.source_server or 'Manual'})"

    @property
    def is_new_arrival(self):
        if self.is_published and self.published_at:
            return self.published_at >= timezone.now() - timedelta(days=7)
        return False

    @property
    def is_discount_active(self):
        now = timezone.now()
        if self.discount in [None, 0]:
            return False
        if self.discount_start and self.discount_end:
            return self.discount_start <= now <= self.discount_end
        return True
    
    @property
    def final_price(self):
        if self.is_discount_active:
            discount_amount = (Decimal(self.discount) / Decimal(100)) * self.price
            return (self.price - discount_amount).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        return self.price

    @property
    def is_visible(self):
        return self.is_published and (self.published_at is None or self.published_at <= timezone.now())

    def update_reviews(self):
        reviews = self.reviews.all()
        self.num_reviews = reviews.count()
        self.average_rating = reviews.aggregate(models.Avg('rating'))['rating__avg'] or 0.0
        self.save()

    def save(self, *args, **kwargs):
        unique_part = uuid.uuid4().hex[:3]
        new_slug = slugify(self.name)
        unique_slug = f"{new_slug}-{unique_part}"       
        current_slug_base = self.slug.rsplit('-', 1)[0] if self.slug else ''
        
        if current_slug_base != new_slug:
            self.slug = unique_slug
        
        if not self.is_discount_active:
            self.discount = 0
        
        super().save(*args, **kwargs)

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
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
