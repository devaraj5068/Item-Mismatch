from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


from rest_framework.permissions import AllowAny

from rest_framework.authtoken.models import Token

class ApiLoginView(APIView):
    # allow any user (even unauthenticated) to hit this endpoint
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        # GET requests just inform the user to use POST
        return Response({"message": "Use POST method to login"})

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Create or get token
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                "message": "Login successful",
                "user": user.username,
                "token": token.key,
                "redirect": "/dashboard/",
            })
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


def login_page(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password'})

    return render(request, 'login.html')


@login_required
def dashboard_page(request):
    return render(request, 'dashboard.html')


def logout_view(request):
    logout(request)
    return redirect('login')
