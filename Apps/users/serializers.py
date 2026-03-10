from .models import CustomUserModel, Profile
from django.contrib.auth import get_user_model
from rest_framework import serializers


# ------------------------------------------------------------------------------
# PROFILE
# ------------------------------------------------------------------------------
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'


# ------------------------------------------------------------------------------
# REGISTRATION
# ------------------------------------------------------------------------------
class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True,
        help_text="User's email address"
    )
    username = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=150,
        help_text="Optional username (if not provided, will be generated from email)"
    )
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        help_text="User's password"
    )

    def validate_email(self, value):
        """Validate that email is not already registered"""
        User = get_user_model()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email already exists.")
        return value


# ------------------------------------------------------------------------------
# VERIFY REGISTRATION OTP
# ------------------------------------------------------------------------------
class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True,
        help_text="Email address used during registration"
    )
    otp = serializers.CharField(
        required=True,
        max_length=6,
        min_length=6,
        help_text="6-digit OTP code sent to your email"
    )


# ------------------------------------------------------------------------------
# RESEND REGISTRATION OTP
# ------------------------------------------------------------------------------
class ResendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True,
        help_text="Email address used during registration"
    )


# ------------------------------------------------------------------------------
# LOGIN
# ------------------------------------------------------------------------------
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True,
        help_text="User's email address"
    )
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        help_text="User's password"
    )


# ------------------------------------------------------------------------------
# LOGOUT
# ------------------------------------------------------------------------------
class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(
        required=True,
        help_text="JWT refresh token to blacklist"
    )


# ------------------------------------------------------------------------------
# FORGOT PASSWORD
# ------------------------------------------------------------------------------
class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True,
        help_text="User's email address"
    )


# ------------------------------------------------------------------------------
# VERIFY FORGOT PASSWORD OTP
# ------------------------------------------------------------------------------
class VerifyForgotPasswordOTPSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True,
        help_text="Email address used during forgot password request"
    )
    otp = serializers.CharField(
        required=True,
        max_length=6,
        min_length=6,
        help_text="6-digit OTP code sent to your email"
    )


# ------------------------------------------------------------------------------
# SET NEW PASSWORD (FORGOT PASSWORD)
# ------------------------------------------------------------------------------
class SetNewPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True,
        help_text="User's email address"
    )
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        help_text="New password for your account"
    )
    confirm_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        help_text="Confirm your new password"
    )

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return data


# ------------------------------------------------------------------------------
# RESET PASSWORD
# ------------------------------------------------------------------------------
class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True,
        help_text="User's email address"
    )
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        help_text="New password for your account"
    )
    confirm_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        help_text="Confirm your new password"
    )

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return data


