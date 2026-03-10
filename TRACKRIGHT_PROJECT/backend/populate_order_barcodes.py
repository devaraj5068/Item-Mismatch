#!/usr/bin/env python
"""
Populate barcode field for existing orders that lack one.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trackright_backend.settings')
django.setup()

from core.models import Order, generate_order_barcode


def populate():
    qs = Order.objects.filter(barcode='')
    print(f"Found {qs.count()} orders without barcode")
    for order in qs:
        order.barcode = generate_order_barcode()
        order.save()
        print(f"Assigned {order.barcode} to order {order.order_number}")
    print("Done.")

if __name__ == '__main__':
    populate()