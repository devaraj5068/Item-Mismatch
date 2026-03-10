from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Product, Order, OrderItem, ScanRecord, MismatchReport, Task

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_barcode = serializers.CharField(source='product.barcode', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product_name', 'product_barcode', 'quantity', 'verified_quantity']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(source='orderitem_set', many=True, read_only=True, required=False)
    created_by_name = serializers.SerializerMethodField()

    def get_created_by_name(self, obj):
        return obj.created_by.username if obj.created_by else 'System'

    class Meta:
        model = Order
        fields = ['id', 'order_number', 'customer_name', 'customer_email', 'customer_phone', 'barcode', 'status', 'location', 'created_at', 'updated_at', 'created_by_name', 'items']

class ScanRecordSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    scanned_by_name = serializers.CharField(source='scanned_by.username', read_only=True)

    class Meta:
        model = ScanRecord
        fields = '__all__'

class MismatchSerializer(serializers.ModelSerializer):
    reported_by_name = serializers.CharField(source='reported_by.username', read_only=True)
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    
    class Meta:
        model = MismatchReport
        fields = '__all__'

class TaskSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.CharField(source='assigned_to.username', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = Task
        fields = '__all__'