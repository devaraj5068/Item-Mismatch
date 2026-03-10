#!/usr/bin/env python
"""
Populate TrackRight database with sample data
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trackright_backend.settings')
django.setup()

from core.models import Product, Order, OrderItem, ScanRecord, MismatchReport, Task
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

def create_sample_data():
    print("Creating sample data for TrackRight...")
    
    # Create test user
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={'email': 'test@trackright.com'}
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print('✓ Test user created')
    
    # Create products with different departments
    products = [
        Product.objects.get_or_create(
            barcode='123456789',
            defaults={'name': 'Laptop', 'sku': 'LAPTOP001', 'description': 'Gaming Laptop', 'department': 'Electronics'}
        )[0],
        Product.objects.get_or_create(
            barcode='987654321',
            defaults={'name': 'Mouse', 'sku': 'MOUSE001', 'description': 'Wireless Mouse', 'department': 'Electronics'}
        )[0],
        Product.objects.get_or_create(
            barcode='456789123',
            defaults={'name': 'Keyboard', 'sku': 'KBD001', 'description': 'Mechanical Keyboard', 'department': 'Electronics'}
        )[0],
        Product.objects.get_or_create(
            barcode='789123456',
            defaults={'name': 'Monitor', 'sku': 'MON001', 'description': '4K Monitor', 'department': 'Electronics'}
        )[0],
        Product.objects.get_or_create(
            barcode='111222333',
            defaults={'name': 'Office Chair', 'sku': 'OFFCHAIR01', 'description': 'Ergonomic office chair', 'department': 'Furniture'}
        )[0],
        Product.objects.get_or_create(
            barcode='444555666',
            defaults={'name': 'Notebook', 'sku': 'NOTE001', 'description': 'Spiral notebook', 'department': 'Stationery'}
        )[0],
        Product.objects.get_or_create(
            barcode='777888999',
            defaults={'name': 'Desk Lamp', 'sku': 'LAMPP01', 'description': 'LED desk lamp', 'department': 'Office Supplies'}
        )[0],
        Product.objects.get_or_create(
            barcode='222333444',
            defaults={'name': 'T-Shirt', 'sku': 'TSHIRT01', 'description': 'Cotton T-Shirt', 'department': 'Clothing'}
        )[0],
    ]
    print(f'✓ {len(products)} products created')
    
    # Create orders
    orders = [
        Order.objects.get_or_create(
            order_number='ORD001',
            defaults={'customer_name': 'John Doe', 'status': 'pending', 'created_by': user}
        )[0],
        Order.objects.get_or_create(
            order_number='ORD002',
            defaults={'customer_name': 'Jane Smith', 'status': 'packed', 'created_by': user}
        )[0],
        Order.objects.get_or_create(
            order_number='ORD003',
            defaults={'customer_name': 'Bob Johnson', 'status': 'shipped', 'created_by': user}
        )[0],
    ]
    print(f'✓ {len(orders)} orders created')
    
    # Create order items
    items_created = 0
    for i, order in enumerate(orders):
        for j in range(2):
            product = products[(i + j) % len(products)]
            OrderItem.objects.get_or_create(
                order=order,
                product=product,
                defaults={'quantity': (j + 1) * 2}
            )
            items_created += 1
    print(f'✓ {items_created} order items created')
    
    # Create scan records
    ScanRecord.objects.get_or_create(
        order=orders[0],
        product=products[0],
        defaults={
            'scanned_barcode': '123456789',
            'expected_barcode': '123456789',
            'is_match': True,
            'scanned_by': user,
            'location': 'Warehouse A'
        }
    )
    ScanRecord.objects.get_or_create(
        order=orders[1],
        product=products[1],
        defaults={
            'scanned_barcode': '987654321',
            'expected_barcode': '987654321',
            'is_match': True,
            'scanned_by': user,
            'location': 'Warehouse A'
        }
    )
    print('✓ Scan records created')
    
    # Create some mismatch reports across departments
    mismatches = []
    # use existing orders and products to generate mismatches
    if products:
        mismatches.append(MismatchReport.objects.get_or_create(
            order=orders[0],
            product=products[0],
            defaults={
                'expected_product': products[1].name,
                'scanned_product': products[0].name,
                'expected_quantity': 1,
                'actual_quantity': 1,
                'status': 'pending',
                'reported_by': user,
                'location': 'Warehouse A'
            }
        )[0])
        # add a mismatch with a Furniture product
        mismatches.append(MismatchReport.objects.get_or_create(
            order=orders[1],
            product=products[4],
            defaults={
                'expected_product': 'Office Chair',
                'scanned_product': 'Office Chair',
                'expected_quantity': 2,
                'actual_quantity': 1,
                'status': 'pending',
                'reported_by': user,
                'location': 'Warehouse B'
            }
        )[0])
        # add a mismatch with a Stationery product
        mismatches.append(MismatchReport.objects.get_or_create(
            order=orders[2],
            product=products[5],
            defaults={
                'expected_product': 'Notebook',
                'scanned_product': 'Notebook',
                'expected_quantity': 5,
                'actual_quantity': 4,
                'status': 'under_review',
                'reported_by': user,
                'location': 'Warehouse A'
            }
        )[0])
        # Add a mismatch for the Clothing department product
        mismatches.append(MismatchReport.objects.get_or_create(
            order=orders[0],
            product=products[7],  # T-Shirt
            defaults={
                'expected_product': 'T-Shirt',
                'scanned_product': 'T-Shirt',
                'expected_quantity': 3,
                'actual_quantity': 2,
                'status': 'pending',
                'reported_by': user,
                'location': 'Warehouse C'
            }
        )[0])
    print(f'✓ {len(mismatches)} mismatch reports created')
    
    # Create tasks
    tasks = [
        Task.objects.get_or_create(
            title='Pack order ORD001',
            defaults={
                'priority': 'high',
                'status': 'pending',
                'created_by': user,
                'due_date': timezone.now().date()
            }
        )[0],
        Task.objects.get_or_create(
            title='Verify inventory',
            defaults={
                'priority': 'medium',
                'status': 'in_progress',
                'created_by': user,
                'due_date': timezone.now().date() + timedelta(days=1)
            }
        )[0],
        Task.objects.get_or_create(
            title='Update shipping labels',
            defaults={
                'priority': 'low',
                'status': 'completed',
                'created_by': user,
                'due_date': timezone.now().date() - timedelta(days=1)
            }
        )[0],
    ]
    print(f'✓ {len(tasks)} tasks created')
    
    print("\n✓ Sample data creation completed successfully!")

if __name__ == '__main__':
    create_sample_data()
