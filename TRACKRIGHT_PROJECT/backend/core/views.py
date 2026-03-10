from rest_framework import viewsets, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.static import serve
from pathlib import Path
import os
from django.utils import timezone
from django.db.models import Q
from .models import Product, Order, OrderItem, ScanRecord, MismatchReport, Task
from .serializers import (
    UserSerializer, ProductSerializer, OrderSerializer, OrderItemSerializer,
    ScanRecordSerializer, MismatchSerializer, TaskSerializer
)

# Template Views
@require_http_methods(["GET"])
def landing_view(request):
    return render(request, 'landing.html')

@require_http_methods(["GET"])
def login_page_view(request):
    return render(request, 'login.html')

@require_http_methods(["GET"])
def dashboard_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'dashboard.html')

@require_http_methods(["GET"])
def orders_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    # load orders for server-side rendering too
    orders = Order.objects.all().order_by('-created_at').prefetch_related('products')
    return render(request, 'orders.html', {'orders': orders})

@require_http_methods(["GET"])
def orders_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'orders.html', {'orders': orders})

@require_http_methods(["GET"])
def scan_verify_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Calculate today's scan statistics
    today = timezone.now().date()
    
    today_scans = ScanRecord.objects.filter(
        scanned_at__date=today
    ).count()
    
    matches = ScanRecord.objects.filter(
        status="verified",
        scanned_at__date=today
    ).count()
    
    mismatches = ScanRecord.objects.filter(
        status="mismatch",
        scanned_at__date=today
    ).count()
    
    context = {
        "scan_mode": "product",
        "today_scans": today_scans,
        "matches": matches,
        "mismatches": mismatches,
    }
    
    return render(request, 'scan_verify.html', context)

@require_http_methods(["POST"])
def verify_barcode(request):
    # require authenticated session
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "message": "Authentication required"}, status=401)

    barcode = request.POST.get('barcode')
    if not barcode:
        return JsonResponse({"success": False, "message": "No barcode provided"})
    
    # attempt to look up a product by barcode instead of order/customer
    try:
        product = Product.objects.get(barcode=barcode)
        # record the successful scan with a product link
        ScanRecord.objects.create(
            product=product,
            barcode=barcode,
            status='verified',
            scanned_by=request.user
        )
        return JsonResponse({
            "success": True,
            "expected_product": product.name,
            "scanned_product": product.name,
            "status": "verified"
        })
    except Product.DoesNotExist:
        # no matching product – record mismatch
        ScanRecord.objects.create(
            barcode=barcode,
            status='mismatch',
            scanned_by=request.user
        )
        return JsonResponse({
            "success": False,
            "expected_product": "Unknown",
            "scanned_product": barcode,
            "status": "mismatch"
        })

@require_http_methods(["GET"])
def mismatches_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    mismatches = MismatchReport.objects.all().order_by('-reported_at').select_related('order', 'product', 'reported_by')
    
    return render(request, 'mismatch_reports.html', {
        'mismatches': mismatches
    })

# Frontend serving view
def frontend_view(request, path=''):
    """Serve frontend files from Django"""
    frontend_dir = Path(__file__).resolve().parent.parent.parent / 'frontend'
    
    if not path:
        path = 'index.html'
    
    file_path = frontend_dir / path
    if file_path.exists():
        return serve(request, path, document_root=str(frontend_dir))
    else:
        # Return index.html for SPA routing
        index_path = frontend_dir / 'index.html'
        if index_path.exists():
            return serve(request, 'index.html', document_root=str(frontend_dir))
        else:
            return HttpResponse("Frontend file not found", status=404)

@require_http_methods(["GET"])
def tasks_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'tasks.html')

@require_http_methods(["GET", "POST"])
def add_mismatch_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.method == "POST":
        order_id = request.POST.get('order')
        product_id = request.POST.get('product')
        expected_product = request.POST.get('expected_product')
        scanned_product = request.POST.get('scanned_product')
        expected_quantity = request.POST.get('expected_quantity', '0')
        actual_quantity = request.POST.get('actual_quantity', '0')
        location = request.POST.get('location', '')
        status = request.POST.get('status', 'pending')
        notes = request.POST.get('notes', '')
        
        try:
            order = Order.objects.get(id=order_id)
            product = Product.objects.get(id=product_id)
            
            MismatchReport.objects.create(
                order=order,
                product=product,
                expected_product=expected_product,
                scanned_product=scanned_product,
                expected_quantity=int(expected_quantity),
                actual_quantity=int(actual_quantity),
                location=location,
                status=status,
                notes=notes,
                reported_by=request.user
            )
            
            return redirect('mismatches')
        except (Order.DoesNotExist, Product.DoesNotExist, ValueError) as e:
            return render(request, 'add_mismatch.html', {
                'orders': Order.objects.all(),
                'products': Product.objects.all(),
                'error': f'Error creating mismatch: {str(e)}'
            })
    
    return render(request, 'add_mismatch.html', {
        'orders': Order.objects.all(),
        'products': Product.objects.all()
    })

@require_http_methods(["GET"])
def mismatch_list_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    search_query = request.GET.get('search', '')
    
    mismatches = MismatchReport.objects.select_related('order', 'product', 'reported_by')
    
    if search_query:
        mismatches = mismatches.filter(
            Q(order__order_number__icontains=search_query) |
            Q(expected_product__icontains=search_query) |
            Q(scanned_product__icontains=search_query) |
            Q(status__icontains=search_query)
        )
    
    mismatches = mismatches.order_by('-reported_at')
    
    data = []
    for mismatch in mismatches:
        data.append({
            'id': mismatch.id,
            'order_number': mismatch.order.order_number,
            'expected_product': mismatch.expected_product,
            'scanned_product': mismatch.scanned_product,
            'status': mismatch.status,
            'reported_at': mismatch.reported_at.isoformat(),
            'reported_by_name': mismatch.reported_by.username if mismatch.reported_by else 'System',
        })
    
    return JsonResponse(data, safe=False)

@require_http_methods(["GET"])
def mismatch_detail_view(request, mismatch_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    try:
        mismatch = MismatchReport.objects.select_related('order', 'product', 'reported_by').get(id=mismatch_id)
        data = {
            'id': mismatch.id,
            'order_number': mismatch.order.order_number,
            'expected_product': mismatch.expected_product,
            'scanned_product': mismatch.scanned_product,
            'status': mismatch.status,
            'reported_at': mismatch.reported_at.isoformat(),
            'reported_by_name': mismatch.reported_by.username if mismatch.reported_by else 'System',
            'notes': mismatch.notes,
            'location': mismatch.location,
        }
        return JsonResponse(data)
    except MismatchReport.DoesNotExist:
        return JsonResponse({'error': 'Mismatch not found'}, status=404)

@require_http_methods(["POST"])
def resolve_mismatch_view(request, mismatch_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    try:
        mismatch = MismatchReport.objects.get(id=mismatch_id)
        mismatch.status = 'resolved'
        mismatch.resolved_at = timezone.now()
        mismatch.save()
        
        return JsonResponse({'success': True, 'message': 'Mismatch resolved successfully'})
    except MismatchReport.DoesNotExist:
        return JsonResponse({'error': 'Mismatch not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# Order Detail, Edit, Delete Views
@require_http_methods(["GET"])
def order_detail_view(request, order_id):
    if not request.user.is_authenticated:
        return redirect('login')
    try:
        order = Order.objects.get(id=order_id)
        order_items = OrderItem.objects.filter(order=order).select_related('product')
        return render(request, 'order_detail.html', {
            'order': order,
            'order_items': order_items
        })
    except Order.DoesNotExist:
        return redirect('orders')

@require_http_methods(["GET", "POST"])
def order_edit_view(request, order_id):
    if not request.user.is_authenticated:
        return redirect('login')
    try:
        order = Order.objects.get(id=order_id)
        
        if request.method == "POST":
            customer_name = request.POST.get('customer_name')
            status = request.POST.get('status')
            customer_email = request.POST.get('customer_email', '')
            customer_phone = request.POST.get('customer_phone', '')
            
            order.customer_name = customer_name
            order.status = status
            order.customer_email = customer_email
            order.customer_phone = customer_phone
            order.save()
            
            return redirect('orders')
        
        return render(request, 'order_edit.html', {'order': order})
    except Order.DoesNotExist:
        return redirect('orders')

@require_http_methods(["GET"])
def order_delete_view(request, order_id):
    if not request.user.is_authenticated:
        return redirect('login')
    try:
        order = Order.objects.get(id=order_id)
        order.delete()
    except Order.DoesNotExist:
        pass
    
    return redirect('orders')

# API Views
def home_view(request):
    return JsonResponse({'message': 'Welcome to TrackRight API'})

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    if user:
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data
        })
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([AllowAny])
def signup_view(request):
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')
    
    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
    
    user = User.objects.create_user(username=username, email=email, password=password)
    token, created = Token.objects.get_or_create(user=user)
    
    return Response({
        'token': token.key,
        'user': UserSerializer(user).data
    }, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile_view(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats_view(request):
    from django.utils import timezone
    from datetime import timedelta
    from django.db.models import Count, Q
    
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    
    # Today's scans
    todays_scans = ScanRecord.objects.filter(scanned_at__date=today).count()
    
    # Verified orders (orders with at least one scan)
    verified_orders = Order.objects.filter(
        scanrecord__scanned_at__date=today
    ).distinct().count()
    
    # Total orders
    total_orders = Order.objects.count()
    
    # Mismatch rate (mismatches today / scans today * 100)
    mismatches_today = MismatchReport.objects.filter(reported_at__date=today).count()
    mismatch_rate = (mismatches_today / todays_scans * 100) if todays_scans > 0 else 0
    
    # Orders by status for chart
    orders_by_status = Order.objects.values('status').annotate(count=Count('id'))
    orders_status_data = {item['status']: item['count'] for item in orders_by_status}
    
    # Weekly scans data for chart
    weekly_scans = []
    for i in range(7):
        date = today - timedelta(days=i)
        count = ScanRecord.objects.filter(scanned_at__date=date).count()
        weekly_scans.append({'date': date.strftime('%Y-%m-%d'), 'scans': count})
    weekly_scans.reverse()
    
    # Mismatches by status for chart
    mismatches_by_status = MismatchReport.objects.values('status').annotate(count=Count('id'))
    mismatches_status_data = {item['status']: item['count'] for item in mismatches_by_status}
    
    # Mismatches by department for chart
    # Group by department field of the related product (fallback to 'Unknown' if missing)
    mismatches_by_dept = MismatchReport.objects.values('product__department').annotate(count=Count('id'))
    mismatches_dept_data = {item['product__department'] or 'Unknown': item['count'] for item in mismatches_by_dept}
    
    return Response({
        'todays_scans': todays_scans,
        'verified_orders': verified_orders,
        'mismatch_rate': round(mismatch_rate, 2),
        'total_orders': total_orders,
        'orders_by_status': orders_status_data,
        'weekly_scans': weekly_scans,
        'mismatches_by_status': mismatches_status_data,
        'mismatches_by_department': mismatches_dept_data
    })

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['order_number', 'customer_name', 'status']
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class ScanRecordViewSet(viewsets.ModelViewSet):
    queryset = ScanRecord.objects.all()
    serializer_class = ScanRecordSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(scanned_by=self.request.user)

class MismatchViewSet(viewsets.ModelViewSet):
    queryset = MismatchReport.objects.all()
    serializer_class = MismatchSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['order__order_number', 'status']
    
    def perform_create(self, serializer):
        serializer.save(reported_by=self.request.user)
    
    def perform_update(self, serializer):
        # Set resolved_at when status changes to resolved
        if serializer.validated_data.get('status') == 'resolved' and self.get_object().status != 'resolved':
            serializer.save(resolved_at=timezone.now())
        else:
            serializer.save()

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'priority', 'status']
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def scan_product_view(request):
    barcode = request.data.get('barcode')
    order_id = request.data.get('order_id')
    
    if not barcode:
        return Response({'error': 'Barcode is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        product = Product.objects.get(barcode=barcode)
    except Product.DoesNotExist:
        # if barcode matches an order, return order info instead of product
        try:
            order_obj = Order.objects.get(barcode=barcode)
            # Create scan record for order verification
            ScanRecord.objects.create(
                order=order_obj,
                barcode=barcode,
                status='verified',
                scanned_by=request.user
            )
            return Response({
                'success': True,
                'status': 'verified',
                'order_id': order_obj.order_number,
                'customer': order_obj.customer_name,
                'expected_product': order_obj.customer_name,
                'scanned_product': order_obj.customer_name,
                'message': f'Order verified: {order_obj.order_number}'
            }, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            pass
        # Create scan record for unknown barcode
        scan_record = ScanRecord.objects.create(
            barcode=barcode,
            status='mismatch',
            scanned_by=request.user
        )
        # Create mismatch report
        mismatch = MismatchReport.objects.create(
            order=order if order_id else None,
            product=None,
            expected_product='Unknown',
            scanned_product='Unknown',
            status='pending',
            reported_by=request.user,
            scan_record=scan_record
        )
        return Response({
            'success': False,
            'status': 'mismatch',
            'message': f'Unknown barcode: {barcode}',
            'scanned_product': 'Unknown',
            'expected_product': 'N/A',
            'mismatch_id': mismatch.id,
            'scan_id': scan_record.id
        }, status=status.HTTP_200_OK)
    
    # If no order specified, just record the scan
    if not order_id:
        scan_record = ScanRecord.objects.create(
            product=product,
            barcode=barcode,
            status='verified',
            scanned_by=request.user
        )
        return Response({
            'success': True,
            'status': 'verified',
            'message': f'Product scanned: {product.name}',
            'scanned_product': product.name,
            'expected_product': 'N/A',
            'scan_id': scan_record.id
        }, status=status.HTTP_200_OK)
    
    # Order specified - check if product is in order
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
    
    order_item = OrderItem.objects.filter(order=order, product=product).first()
    if not order_item:
        # Product not in order - mismatch
        scan_record = ScanRecord.objects.create(
            order=order,
            product=product,
            barcode=barcode,
            status='mismatch',
            scanned_by=request.user
        )
        # Create mismatch report
        mismatch = MismatchReport.objects.create(
            order=order,
            product=product,
            expected_product='Not in order',
            scanned_product=product.name,
            status='pending',
            reported_by=request.user,
            scan_record=scan_record
        )
        return Response({
            'success': False,
            'status': 'mismatch',
            'message': f'Product {product.name} not in order',
            'scanned_product': product.name,
            'expected_product': 'Not in order',
            'mismatch_id': mismatch.id,
            'scan_id': scan_record.id
        }, status=status.HTTP_200_OK)
    
    # Product is in order - verified
    scan_record = ScanRecord.objects.create(
        order=order,
        product=product,
        barcode=barcode,
        status='verified',
        scanned_by=request.user
    )
    
    return Response({
        'success': True,
        'status': 'verified',
        'message': f'Product {product.name} verified',
        'scanned_product': product.name,
        'expected_product': product.name,
        'scan_id': scan_record.id
    }, status=status.HTTP_200_OK)

# API ViewSets
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'barcode']

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['order_number', 'customer_name']

class ScanRecordViewSet(viewsets.ModelViewSet):
    queryset = ScanRecord.objects.all()
    serializer_class = ScanRecordSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['barcode', 'order__order_number']
    ordering_fields = ['scanned_at']

class MismatchViewSet(viewsets.ModelViewSet):
    queryset = MismatchReport.objects.all()
    serializer_class = MismatchSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['order__order_number', 'status']
    
    def perform_create(self, serializer):
        serializer.save(reported_by=self.request.user)
    
    def perform_update(self, serializer):
        # Set resolved_at when status changes to resolved
        if serializer.validated_data.get('status') == 'resolved' and self.get_object().status != 'resolved':
            serializer.save(resolved_at=timezone.now())
        else:
            serializer.save()

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'priority', 'status']
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)