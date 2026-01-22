from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ProfileViewSet,
    RegisterAPI,
    VerifyOTPView,
    LoginAPI,
    LogoutAPIView,
    ForgotPasswordAPI,
    VerifyForgotPasswordOTPView,
    SetNewPasswordAPI,
    ResetPasswordAPI,
)

router = DefaultRouter()
router.register(r'profiles', ProfileViewSet, basename='profile')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/register/', RegisterAPI.as_view(), name='auth-register'),
    path('auth/verify-otp/', VerifyOTPView.as_view(), name='auth-verify-otp'),
    path('auth/login/', LoginAPI.as_view(), name='auth-login'),
    path('auth/logout/', LogoutAPIView.as_view(), name='auth-logout'),
    path('auth/forgot-password/', ForgotPasswordAPI.as_view(), name='auth-forgot-password'),
    path('auth/verify-forgot-password-otp/', VerifyForgotPasswordOTPView.as_view(), name='auth-verify-forgot-password-otp'),
    path('auth/set-new-password/', SetNewPasswordAPI.as_view(), name='auth-set-new-password'),
    path('auth/reset-password/', ResetPasswordAPI.as_view(), name='auth-reset-password'),
]
