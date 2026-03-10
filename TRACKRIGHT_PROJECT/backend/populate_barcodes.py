#!/usr/bin/env python
"""
Script to populate barcodes for existing products
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trackright_backend.settings')
django.setup()

from core.models import Product

def populate_barcodes():
    products = Product.objects.filter(barcode='')
    print(f'Found {products.count()} products without barcodes')

    updated = 0
    for product in products:
        product.save()  # This will trigger the save method which generates barcode
        updated += 1
        print(f'Updated product: {product.name} -> {product.barcode}')

    print(f'Successfully updated {updated} products')

if __name__ == '__main__':
    populate_barcodes()