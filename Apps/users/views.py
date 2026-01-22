from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils.decorators import method_decorator

from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client

from allauth.socialaccount.providers.apple.views import AppleOAuth2Adapter
from allauth.socialaccount.providers.apple.client import AppleOAuth2Client

from dj_rest_auth.registration.views import SocialLoginView

from .models import (
    Profile,
    PendingUser,
    ForgotPasswordRequest,
)

from .serializers import (
    RegisterSerializer,
    VerifyOTPSerializer,
    LoginSerializer,
    LogoutSerializer,
    ForgotPasswordSerializer,
    VerifyForgotPasswordOTPSerializer,
    ResetPasswordSerializer,
    SetNewPasswordSerializer,
    ProfileSerializer,
)


# ------------------------------------------------------------------------------
# PROFILE
# ------------------------------------------------------------------------------
@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_summary="List all profiles",
    operation_description="Get a list of all profile entries.",
    tags=['Profile']
))
@method_decorator(name='create', decorator=swagger_auto_schema(
    operation_summary="Create profile",
    operation_description="Create a new profile entry.",
    tags=['Profile']
))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(
    operation_summary="Get profile details",
    operation_description="Get details of a specific profile entry by ID.",
    tags=['Profile']
))
@method_decorator(name='update', decorator=swagger_auto_schema(
    operation_summary="Update profile",
    operation_description="Update a specific profile entry by ID.",
    tags=['Profile']
))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(
    operation_summary="Partially update profile",
    operation_description="Partially update a specific profile entry by ID.",
    tags=['Profile']
))
@method_decorator(name='destroy', decorator=swagger_auto_schema(
    operation_summary="Delete profile",
    operation_description="Delete a specific profile entry by ID.",
    tags=['Profile']
))
class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]    


# ------------------------------------------------------------------------------
# REGISTRATION
# ------------------------------------------------------------------------------
class RegisterAPI(APIView):
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_summary="Register new user",
        operation_description="Register a new user account. An OTP will be sent to the provided email for verification. The OTP expires in 15 minutes.",
        tags=['Authentication'],
        request_body=RegisterSerializer,
        responses={
            201: openapi.Response(
                description="OTP sent successfully",
                examples={
                    "application/json": {
                        "message": "OTP sent to your email. Verify to complete registration."
                    }
                }
            ),
            400: openapi.Response(
                description="Bad Request",
                examples={
                    "application/json": {
                        "error": "User already exists."
                    }
                }
            )
        }
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]
        username = serializer.validated_data.get("username", "")

        User = get_user_model()
        if User.objects.filter(email=email).exists():
            return Response({"error": "User already exists."}, status=status.HTTP_400_BAD_REQUEST)

        pending_user, created = PendingUser.objects.get_or_create(email=email)
        pending_user.password = password
        pending_user.username = username if username else ""
        otp = pending_user.generate_otp()  
        pending_user.save()

        send_mail(
            subject="Your Nowlii verification code",
            message=f"Your OTP code is {otp}. It expires in 15 minutes.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )
        return Response({"message": "OTP sent to your email. Verify to complete registration."}, status=status.HTTP_201_CREATED)


# ------------------------------------------------------------------------------
# VERIFY REGISTRATION OTP
# ------------------------------------------------------------------------------
class VerifyOTPView(APIView):
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_summary="Verify Register OTP",
        operation_description="Verify the 6-digit OTP code sent to your email to complete user registration. OTP codes expire after 15 minutes.",
        tags=['Authentication'],
        request_body=VerifyOTPSerializer,
        responses={
            200: openapi.Response(
                description="Registration completed",
                examples={
                    "application/json": {
                        "message": "Registration complete. You can now log in."
                    }
                }
            ),
            400: openapi.Response(
                description="Bad Request - Invalid or expired OTP",
                examples={
                    "application/json": {
                        "error": "Invalid or expired OTP."
                    }
                }
            ),
            404: openapi.Response(
                description="Pending registration not found",
                examples={
                    "application/json": {
                        "error": "Pending registration not found."
                    }
                }
            )
        }
    )
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data["email"]
        otp = serializer.validated_data["otp"]

        pending = PendingUser.objects.filter(email=email).first()
        if not pending:
            return Response({"error": "Pending registration not found."}, status=status.HTTP_404_NOT_FOUND)

        ok, msg = pending.verify_otp(otp)
        if not ok:
            return Response({"error": msg}, status=status.HTTP_400_BAD_REQUEST)

        raw_password = pending.password

        User = get_user_model()
        
        if pending.username:
            username = pending.username
        else:
            username = email.split("@")[0].lower()

        user = User.objects.create_user(username=username, email=email, password=raw_password)
        user.is_active = True
        user.save()
        pending.delete()

        return Response({"message": "Registration complete. You can now log in."}, status=status.HTTP_200_OK)


# ------------------------------------------------------------------------------
# LOGIN
# ------------------------------------------------------------------------------
class LoginAPI(APIView):
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_summary="User login",
        operation_description="Authenticate with email and password to receive JWT access and refresh tokens. Use the access token for authenticated API requests.",
        tags=['Authentication'],
        request_body=LoginSerializer,
        responses={
            200: openapi.Response(
                description="Login successful",
                examples={
                    "application/json": {
                        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTY0...",
                        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjQ...",
                        "user": {
                            "user_id": 1,
                            "email": "john.doe@example.com",
                            "username": "johndoe",
                            "is_superuser": False
                        }
                    }
                }
            ),
            400: openapi.Response(
                description="Bad Request - Missing credentials",
                examples={
                    "application/json": {
                        "email": ["This field is required."],
                        "password": ["This field is required."]
                    }
                }
            ),
            401: openapi.Response(
                description="Unauthorized - Invalid credentials",
                examples={
                    "application/json": {
                        "error": "Invalid credentials."
                    }
                }
            )
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        try:
            user = get_user_model().objects.get(email=email)
        except get_user_model().DoesNotExist:
            return Response({'error': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)
        
        if not user.check_password(password):
            return Response({'error': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token

        return Response({
            'refresh': str(refresh),
            'access': str(access_token),
            'user': {
                'user_id': user.id,
                'email': user.email,
                'username': user.username,
                'is_superuser': user.is_superuser
            }
        })


# ------------------------------------------------------------------------------
# LOGOUT
# ------------------------------------------------------------------------------
class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_summary="User logout",
        operation_description="Logout by blacklisting the JWT refresh token. After logout, the refresh token cannot be used to obtain new access tokens.",
        tags=['Authentication'],
        request_body=LogoutSerializer,
        responses={
            200: openapi.Response(
                description="Logout successful",
                examples={
                    "application/json": {
                        "message": "Logged out successfully"
                    }
                }
            ),
            400: openapi.Response(
                description="Bad Request - Invalid token",
                examples={
                    "application/json": {
                        "error": "Token is invalid or expired"
                    }
                }
            ),
            401: "Unauthorized - Authentication required"
        }
    )
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            refresh_token = serializer.validated_data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()  
            return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ------------------------------------------------------------------------------
# FORGOT PASSWORD
# ------------------------------------------------------------------------------
class ForgotPasswordAPI(APIView):
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_summary="Forgot password",
        operation_description="Request password reset. An OTP will be sent to the provided email. OTP expires in 15 minutes.",
        tags=['Authentication'],
        request_body=ForgotPasswordSerializer,
        responses={
            200: openapi.Response(
                description="OTP sent successfully",
                examples={
                    "application/json": {
                        "message": "OTP sent to your email."
                    }
                }
            ),
            404: openapi.Response(
                description="User not found",
                examples={
                    "application/json": {
                        "error": "User with this email does not exist."
                    }
                }
            )
        }
    )
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data["email"]
        
        User = get_user_model()
        if not User.objects.filter(email=email).exists():
            return Response({"error": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)
        
        forgot_request, created = ForgotPasswordRequest.objects.get_or_create(email=email)
        otp = forgot_request.generate_otp()
        
        send_mail(
            subject="Your Nowlii password reset code",
            message=f"Your OTP code is {otp}. It expires in 15 minutes.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )
        return Response({"message": "OTP sent to your email."}, status=status.HTTP_200_OK)


# ------------------------------------------------------------------------------
# VERIFY FORGOT PASSWORD OTP
# ------------------------------------------------------------------------------
class VerifyForgotPasswordOTPView(APIView):
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_summary="Verify Forgot Password OTP",
        operation_description="Verify the OTP sent to your email for Forgot password.",
        tags=['Authentication'],
        request_body=VerifyForgotPasswordOTPSerializer,
        responses={
            200: openapi.Response(
                description="OTP verified successfully",
                examples={
                    "application/json": {
                        "message": "OTP verified successfully. You can now reset your password."
                    }
                }
            ),
            400: openapi.Response(
                description="Bad Request - Invalid or expired OTP",
                examples={
                    "application/json": {
                        "error": "Invalid OTP"
                    }
                }
            ),
            404: openapi.Response(
                description="Password reset request not found",
                examples={
                    "application/json": {
                        "error": "Password reset request not found."
                    }
                }
            )
        }
    )
    def post(self, request):
        serializer = VerifyForgotPasswordOTPSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data["email"]
        otp = serializer.validated_data["otp"]
        
        forgot_request = ForgotPasswordRequest.objects.filter(email=email).first()
        if not forgot_request:
            return Response({"error": "Password reset request not found."}, status=status.HTTP_404_NOT_FOUND)
        
        ok, msg = forgot_request.verify_otp(otp)
        if not ok:
            return Response({"error": msg}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({"message": "OTP verified successfully. You can now reset your password."}, status=status.HTTP_200_OK)


# ------------------------------------------------------------------------------
# SET NEW PASSWORD (FORGOT PASSWORD)
# ------------------------------------------------------------------------------
class SetNewPasswordAPI(APIView):
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_summary="Set new password (Forgot Password)",
        operation_description="Set a new password after verifying the OTP sent to your email. This endpoint is specifically for the forgot password flow.",
        tags=['Authentication'],
        request_body=SetNewPasswordSerializer,
        responses={
            200: openapi.Response(
                description="Password set successfully",
                examples={
                    "application/json": {
                        "message": "Password has been reset successfully."
                    }
                }
            ),
            400: openapi.Response(
                description="Bad Request",
                examples={
                    "application/json": {
                        "error": "No password reset request found. Please request a new OTP."
                    }
                }
            ),
            404: openapi.Response(
                description="User not found",
                examples={
                    "application/json": {
                        "error": "User with this email does not exist."
                    }
                }
            )
        }
    )
    def post(self, request):
        serializer = SetNewPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data["email"]
        new_password = serializer.validated_data["new_password"]
        
        forgot_request = ForgotPasswordRequest.objects.filter(email=email).first()
        if not forgot_request:
            return Response({"error": "No password reset request found. Please request a new OTP."}, status=status.HTTP_400_BAD_REQUEST)

        if not forgot_request.otp:
            return Response({"error": "Please verify your OTP first."}, status=status.HTTP_400_BAD_REQUEST)
        
        User = get_user_model()
        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"error": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)
        
        user.set_password(new_password)
        user.save()
        
        forgot_request.delete()
        
        return Response({"message": "Password has been reset successfully."}, status=status.HTTP_200_OK)


# ------------------------------------------------------------------------------
# RESET PASSWORD
# ------------------------------------------------------------------------------
class ResetPasswordAPI(APIView):
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_summary="Reset password",
        operation_description="Reset your password after logging in. Requires new_password and confirm_password fields.",
        tags=['Authentication'],
        request_body=ResetPasswordSerializer,
        responses={
            200: openapi.Response(
                description="Password changed successfully",
                examples={
                    "application/json": {
                        "message": "Password changed successfully."
                    }
                }
            ),
            400: openapi.Response(
                description="Bad Request",
                examples={
                    "application/json": {
                        "error": "Passwords do not match."
                    }
                }
            ),
            401: "Unauthorized - Authentication required"
        }
    )
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data["email"]
        new_password = serializer.validated_data["new_password"]
        
        User = get_user_model()
        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"error": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)
        
        user.set_password(new_password)
        user.save()
        
        return Response({"message": "Password changed successfully."}, status=status.HTTP_200_OK)



# ------------------------------------------------------------------------------
# SOCIAL AUTHENTICATION GOOGLE
# ------------------------------------------------------------------------------
class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    client_class = OAuth2Client


# ------------------------------------------------------------------------------
# SOCIAL AUTHENTICATION APPLE
# ------------------------------------------------------------------------------
class AppleLogin(SocialLoginView):
    adapter_class = AppleOAuth2Adapter
    client_class = AppleOAuth2Client
