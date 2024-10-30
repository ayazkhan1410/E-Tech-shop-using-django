from django.db import models
from django.contrib.auth.models import AbstractUser
from .helpers import Manager
from django.utils.text import slugify
import string
import random
import uuid
# Create your models here.

class CustomUser(AbstractUser):
    username = None
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=100)
    address = models.TextField()
    user_profile = models.ImageField(upload_to='user_profile/', default='user_profile/default.webp')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = Manager()        

    def get_cart_count(self):
        total_items = 0
        cart_items = Cart.objects.filter(user=self, is_ordered=False)
        for item in cart_items:
            total_items += item.quantity
        return total_items
    
    def __str__(self) -> str:
        return self.email

class Category(models.Model):
    category = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.category

class Company(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='companies', null=True, blank=True)
    company = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-company']

    def __str__(self):
        return self.company

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='products')
    product_name = models.CharField(max_length=100)
    product_description = models.TextField()
    orignal_price = models.PositiveIntegerField(default=0)
    discount_percentage = models.PositiveIntegerField(default=0)
    discounted_price = models.PositiveIntegerField(default=0)
    warranty = models.IntegerField(default=1)
    product_image = models.ImageField(upload_to='product_images/')
    is_stock = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    is_trending = models.BooleanField(default=False)
    slug = models.SlugField(blank=True, null=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def discounted_price(self):
        
        discount_amount = (float(self.discount_percentage) / 100) * float(self.orignal_price)
        discounted_price = float(self.orignal_price) - discount_amount
        formatted_discounted_price = "{:.2f}".format(round(discounted_price, 2))
        return formatted_discounted_price

    def formatted_price(self):
        return "{:.2f}".format(self.orignal_price)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.product_name)
        super(Product, self).save(*args, **kwargs)

    def __str__(self):
        return self.product_name

class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    subject = models.CharField(max_length=100)
    message = models.TextField()

    def __str__(self):
        return self.email

class FeatureProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='feature_product_images')
    image = models.ImageField(upload_to='feature_product_images/')

    def __str__(self):
        return self.product.product_name

class ProductDescription(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_descriptions')
    feature = models.CharField(max_length=100)
    product_description = models.TextField()
    product_image = models.ImageField(upload_to='product_description_images/')

    def __str__(self) -> str:
        return self.product.product_name

class AdditionalInformation(models.Model):
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='additional_informations')
    new_product_name = models.CharField(max_length=100, blank=True, null=True)
    feature = models.CharField(max_length=100)
    exisiting_product_description1 = models.TextField(null = True, blank = True)
    new_product_description = models.TextField(null = True, blank = True)

    class Meta:
        ordering = ['feature']
        
    def __str__(self) -> str:
        return f"{self.product.product_name} - {self.feature}"

class StayInTouch(models.Model):
    email = models.EmailField(max_length=100, null=True, blank=True)

class Cart(models.Model):
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_carts')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_carts')
    quantity = models.PositiveIntegerField(default=1)
    is_ordered = models.BooleanField(default=False)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def mark_as_ordered_or_deleted(self):
            if not self.is_ordered:
                self.is_ordered = True
                self.save()

    def __str__(self):
        return self.user.email
    
status = ((1, 'Add to Cart'), (2, 'Placed'), (3, 'Shipped'), (4, 'Delivered'), (5, 'Cancelled'), (6, 'Returned'), (7, 'Refunded'))
class OrderTracking(models.Model):
    
    order_id = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_orders')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_orders')
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    order_status = models.PositiveIntegerField(choices=status, default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def generate_order_id(self):
        self.order_id = str(uuid.uuid4())[:10].upper()
    
    def save(self, *args, **kwargs):
        if not self.order_id:
            self.generate_order_id()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.user.email

class ShippingAddress(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    area_code = models.CharField(max_length=100)
    primary_phone = models.CharField(max_length=100)
    street_address = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=100)

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_review')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_reviews')
    name = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    review = models.TextField()
    rating = models.PositiveIntegerField(default = 1)

class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    forget_token = models.CharField(max_length=100, blank=True, null=True)