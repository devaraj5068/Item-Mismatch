from django.urls import path
from . import views
from core import views as core_views

urlpatterns = [
    path('login/', views.login_page, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_page, name='dashboard'),

    # Orders management
    path('orders/', core_views.orders_view, name='orders'),
    path('orders/view/<int:order_id>/', core_views.order_detail_view, name='order_detail'),
    path('orders/edit/<int:order_id>/', core_views.order_edit_view, name='order_edit'),
    path('orders/delete/<int:order_id>/', core_views.order_delete_view, name='order_delete'),

    # additional pages accessible after login
    path('scan-verify/', core_views.scan_verify_view, name='scan_verify'),
    path('mismatches/', core_views.mismatches_view, name='mismatches'),
    path('tasks/', core_views.tasks_view, name='tasks'),

    # API endpoint for login
    path('api/login/', views.ApiLoginView.as_view(), name='api_login'),
]
