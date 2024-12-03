"""
Definition of models to the application.
"""

# Django imports.
from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name
    

class Product(models.Model):

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')

    def __str__(self) -> str:
        return self.name
    

class Customer(models.Model):

    class Meta:
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'

    GENDER_CHOICES = (
        ('F', 'Female'),
        ('M', 'Male'),
    )

    document_id = models.CharField(max_length=12)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='F')
    phone = models.CharField(max_length=20)
    birthdate = models.DateField(null=True, blank=True)
    address = models.TextField()
    user = models.OneToOneField(User, on_delete=models.RESTRICT)

    def __str__(self):
        return f'{self.user.first_name} - {self.document_id}'
    

class Order(models.Model):

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
    
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Delivered', 'Delivered'),
        ('Canceled', 'Canceled'),
        ('Rejected', 'Rejected'),
    )
         
    order_number = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    customer = models.ForeignKey(Customer, on_delete=models.RESTRICT, related_name='orders')

    def __str__(self):
        return self.order_number
    

class OrderDetail(models.Model):
    
    class Meta:
        verbose_name = 'Order Detail'
        verbose_name_plural = 'Order Details'

    quantity = models.SmallIntegerField(default=1)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    order = models.ForeignKey(Order, on_delete=models.RESTRICT, related_name='details')
    product = models.ForeignKey(Product, on_delete=models.RESTRICT, related_name='order_details')

    def __str__(self):
        return self.product.name
