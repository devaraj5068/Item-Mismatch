from django.db import models
from django.contrib.auth.models import User
import random
import string

def generate_barcode():
    """Generate a unique alphanumeric barcode"""
    characters = string.ascii_uppercase + string.digits
    while True:
        barcode = ''.join(random.choice(characters) for _ in range(10))
        if not Product.objects.filter(barcode=barcode).exists():
            return barcode

class Product(models.Model):
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=100, unique=True)
    barcode = models.CharField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    quantity = models.IntegerField(default=0)
    department = models.CharField(max_length=100, default='General')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.barcode:
            self.barcode = generate_barcode()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

# helper for order-specific barcode

def generate_order_barcode():
    characters = string.ascii_uppercase + string.digits
    while True:
        code = ''.join(random.choice(characters) for _ in range(10))
        if not Order.objects.filter(barcode=code).exists():
            return code

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('packed', 'Packed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('mismatch', 'Mismatch'),
    ]
    order_number = models.CharField(max_length=100, unique=True)
    customer_name = models.CharField(max_length=255)
    customer_email = models.EmailField(blank=True)
    customer_phone = models.CharField(max_length=20, blank=True)
    products = models.ManyToManyField(Product, through='OrderItem')
    barcode = models.CharField(max_length=20, unique=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    location = models.CharField(max_length=100, default='Warehouse A')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='orders_created')

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.barcode:
            self.barcode = generate_order_barcode()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_number

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    verified_quantity = models.IntegerField(default=0)

class ScanRecord(models.Model):
    STATUS_CHOICES = [
        ('verified', 'Verified'),
        ('mismatch', 'Mismatch'),
        ('pending', 'Pending'),
    ]
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    barcode = models.CharField(max_length=100, blank=True, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='verified')
    # Legacy fields (kept for backward compatibility)
    scanned_barcode = models.CharField(max_length=100, blank=True)
    expected_barcode = models.CharField(max_length=100, blank=True)
    is_match = models.BooleanField(default=True)
    # End legacy fields
    scanned_at = models.DateTimeField(auto_now_add=True)
    scanned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    location = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['-scanned_at']
    
    def __str__(self):
        if self.product:
            return f"Scan: {self.product.name} - {self.status}"
        elif self.order:
            return f"Order Scan: {self.order.order_number} - {self.status}"
        else:
            return f"Scan: {self.barcode} - {self.status}"

class MismatchReport(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('under_review', 'Under Review'),
        ('resolved', 'Resolved'),
    ]
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    scan_record = models.ForeignKey(ScanRecord, on_delete=models.SET_NULL, null=True)
    expected_product = models.CharField(max_length=255, default='Unknown')
    scanned_product = models.CharField(max_length=255, default='Unknown')
    expected_quantity = models.IntegerField(default=0)
    actual_quantity = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    location = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    reported_at = models.DateTimeField(auto_now_add=True)
    reported_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-reported_at']

class Task(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assigned_tasks')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_tasks')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title