"""
URL configuration for trackright_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from core.views import (
    landing_view, dashboard_view, orders_view, scan_verify_view, verify_barcode, mismatches_view, tasks_view,
    order_detail_view, order_edit_view, order_delete_view, add_mismatch_view, resolve_mismatch_view, mismatch_detail_view, mismatch_list_view,
    frontend_view
)
from django.views.static import serve
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

urlpatterns = [
    # Template views
    path('', landing_view, name='landing'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('orders/', orders_view, name='orders'),
    path('orders/view/<int:order_id>/', order_detail_view, name='order_view'),
    path('orders/edit/<int:order_id>/', order_edit_view, name='order_edit'),
    path('orders/delete/<int:order_id>/', order_delete_view, name='order_delete'),
    path('scan-verify/', scan_verify_view, name='scan_verify'),
    # verify API accessible at root path as well
    path('scan/verify/', verify_barcode, name='verify_barcode'),
    path('mismatches/', mismatches_view, name='mismatches'),
    path('mismatches/add/', add_mismatch_view, name='add_mismatch'),
    path('mismatches/list/', mismatch_list_view, name='mismatch_list'),
    path('mismatches/detail/<int:mismatch_id>/', mismatch_detail_view, name='mismatch_detail'),
    path('mismatches/resolve/<int:mismatch_id>/', resolve_mismatch_view, name='resolve_mismatch'),
    path('tasks/', tasks_view, name='tasks'),
    
    # Accounts
    path('', include('accounts.urls')),
    path('accounts/', include('accounts.urls')),
    
    # Admin
    path('admin/', admin.site.urls),
    
    # API routes
    path('api/', include('core.urls')),
    
    # Serve frontend files
    path('app/', frontend_view, name='frontend'),
    path('app/<path:path>', frontend_view, name='frontend_path'),
]


