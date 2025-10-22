from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.conf import settings
from drf_spectacular.utils import extend_schema
from application.throttles import (
    LoginRateThrottle, RegisterRateThrottle, BurstRateThrottle, 
    MediumSecurityThrottle, HighSecurityThrottle
)
from .serializers import UserRegistrationSerializer, UserSerializer, CustomTokenObtainPairSerializer

User = get_user_model()


class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    throttle_classes = [RegisterRateThrottle, BurstRateThrottle]

    @extend_schema(
        summary="Register a new user",
        description="Create a new user account with email and password",
        responses={201: UserSerializer}
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Return user data without tokens for registration
        return Response(
            UserSerializer(user).data,
            status=status.HTTP_201_CREATED
        )


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle, BurstRateThrottle]

    @extend_schema(
        summary="Login user",
        description="Authenticate user and return access token in response and refresh token in HTTP-only cookie",
        responses={200: CustomTokenObtainPairSerializer}
    )
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            # Extract refresh token from response data
            refresh_token = response.data.get('refresh')
            
            # Remove refresh token from response data
            response.data.pop('refresh', None)
            
            # Set refresh token as HTTP-only cookie
            response.set_cookie(
                'refresh_token',
                refresh_token,
                max_age=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'],
                httponly=True,  # Prevents JavaScript access
                secure=settings.SIMPLE_JWT.get('AUTH_COOKIE_SECURE', False),
                samesite=settings.SIMPLE_JWT.get('AUTH_COOKIE_SAMESITE', 'Lax')
            )
        
        return response


class CustomTokenRefreshView(TokenRefreshView):
    permission_classes = [AllowAny]
    throttle_classes = [HighSecurityThrottle, BurstRateThrottle]

    @extend_schema(
        summary="Refresh access token",
        description="Use refresh token from HTTP-only cookie to get new access token",
        responses={200: {"type": "object", "properties": {"access": {"type": "string"}}}}
    )
    def post(self, request, *args, **kwargs):
        # Get refresh token from cookie
        refresh_token = request.COOKIES.get('refresh_token')
        
        if not refresh_token:
            return Response(
                {'error': 'Refresh token not found in cookies'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Add refresh token to request data
        request.data['refresh'] = refresh_token
        
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            # If rotation is enabled, set new refresh token in cookie
            new_refresh = response.data.get('refresh')
            if new_refresh:
                response.set_cookie(
                    'refresh_token',
                    new_refresh,
                    max_age=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'],
                    httponly=True,
                    secure=settings.SIMPLE_JWT.get('AUTH_COOKIE_SECURE', False),
                    samesite=settings.SIMPLE_JWT.get('AUTH_COOKIE_SAMESITE', 'Lax')
                )
                # Remove refresh token from response data
                response.data.pop('refresh', None)
        
        return response


@extend_schema(
    summary="Get current user profile",
    description="Retrieve the authenticated user's profile information",
    responses={200: UserSerializer}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@throttle_classes([MediumSecurityThrottle])
def user_profile(request):
    """Get current user profile (/me endpoint)"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@extend_schema(
    summary="Logout user",
    description="Logout user by clearing refresh token cookie",
    responses={200: {"type": "object", "properties": {"message": {"type": "string"}}}}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([MediumSecurityThrottle])
def logout_view(request):
    """Logout user by clearing refresh token cookie"""
    response = Response({'message': 'Successfully logged out'}, status=status.HTTP_200_OK)
    response.delete_cookie('refresh_token')
    return response


