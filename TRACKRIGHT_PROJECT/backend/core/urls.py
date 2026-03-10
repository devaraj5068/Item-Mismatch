from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'products', views.ProductViewSet)
router.register(r'orders', views.OrderViewSet)
router.register(r'scans', views.ScanRecordViewSet)
router.register(r'mismatches', views.MismatchViewSet)
router.register(r'tasks', views.TaskViewSet)

urlpatterns = [
    # API Views
    path('user/profile/', views.user_profile_view, name='user_profile'),
    path('dashboard/stats/', views.dashboard_stats_view, name='dashboard_stats'),
    path('scan/', views.scan_product_view, name='scan_product'),
    path('scan/verify/', views.verify_barcode, name='verify_barcode'),
    path('', include(router.urls)),
]