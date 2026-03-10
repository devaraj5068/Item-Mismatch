from django.contrib import admin
from .models import Product, Order, OrderItem, ScanRecord, MismatchReport, Task

admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(ScanRecord)
admin.site.register(MismatchReport)
admin.site.register(Task)