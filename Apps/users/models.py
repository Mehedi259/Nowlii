from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.db import models
import random


# ------------------------------------------------------------------------------
# CUSTOM USER MANAGER
# ------------------------------------------------------------------------------
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if not password:
            raise ValueError("Superuser must have a password.")
        return self.create_user(email, password, **extra_fields)


# ------------------------------------------------------------------------------
# CUSTOM USER MODEL
# ------------------------------------------------------------------------------
class CustomUserModel(AbstractBaseUser, PermissionsMixin):
    class Meta:
        app_label = 'users'
        swappable = 'AUTH_USER_MODEL'

    CURRENT_PLAN_CHOICES = [
        ('free', 'free'),
        ('monthly', 'monthly'),
        ('yearly', 'yearly'),
    ]

    LANGUAGE_CHOICES = [
        ('English', 'English'),
        ('Deutsch', 'Deutsch'),
        ('Espanol', 'Espanol'),
    ]

    email = models.EmailField(unique=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    language = models.CharField(max_length=50, choices=LANGUAGE_CHOICES, default='English', blank=True, null=True)
    is_active = models.BooleanField(default=False)  
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)

    paid_user = models.BooleanField(default=False)
    current_plan = models.CharField(max_length=20, choices=CURRENT_PLAN_CHOICES, default='free')
    current_period_start = models.DateTimeField(blank=True, null=True)
    current_period_end = models.DateTimeField(blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    def is_subscribed(self):
        """Check if user has an active subscription."""
        return self.paid_user and self.current_plan != 'free'

    def get_subscription_period(self):
        """Returns subscription period in human-readable format."""
        if self.current_period_start and self.current_period_end:
            return f"{self.current_period_start} - {self.current_period_end}"
        return "No active subscription"


# ------------------------------------------------------------------------------
# PENDING USER
# ------------------------------------------------------------------------------
class PendingUser(models.Model):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, blank=True, null=True)
    password = models.CharField(max_length=255)  
    otp = models.CharField(max_length=6, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)

    OTP_TTL_SECONDS = 15 * 60  # 15 minutes

    def __str__(self):
        return self.email

    def generate_otp(self):
        self.otp = f"{random.randint(0, 999999):06d}"
        self.otp_created_at = timezone.now()
        self.save(update_fields=["otp", "otp_created_at"])
        return self.otp

    def verify_otp(self, otp):
        if not self.otp or not self.otp_created_at:
            return False, "No OTP requested"
        if (timezone.now() - self.otp_created_at).total_seconds() > self.OTP_TTL_SECONDS:
            return False, "OTP expired"
        if str(self.otp) != str(otp):
            return False, "Invalid OTP"
        return True, None


# ------------------------------------------------------------------------------
# FORGOT PASSWORD OTP
# ------------------------------------------------------------------------------
class ForgotPasswordRequest(models.Model):
    email = models.EmailField(unique=True)
    otp = models.CharField(max_length=6, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)

    OTP_TTL_SECONDS = 15 * 60  # 15 minutes

    def __str__(self):
        return self.email

    def generate_otp(self):
        self.otp = f"{random.randint(0, 999999):06d}"
        self.otp_created_at = timezone.now()
        self.save(update_fields=["otp", "otp_created_at"])
        return self.otp

    def verify_otp(self, otp):
        if not self.otp or not self.otp_created_at:
            return False, "No OTP requested"
        if (timezone.now() - self.otp_created_at).total_seconds() > self.OTP_TTL_SECONDS:
            return False, "OTP expired"
        if str(self.otp) != str(otp):
            return False, "Invalid OTP"
        return True, None


# ------------------------------------------------------------------------------
# PROFILE
# ------------------------------------------------------------------------------
class Profile(models.Model):

    GENDER_CHOICES = [
        ('I’m a man', 'I’m a man'),
        ('I’m a woman', 'I’m a woman'),
        ('Another gender', 'Another gender'), 
    ]

    NOWLII_NAME_CHOICES = [
        ('milo', 'milo'),
        ('bloop', 'bloop'),
        ('gumo', 'gumo'),
        ('knotty', 'knotty'),
        ('Fizzy', 'Fizzy'),
        ('zee', 'zee'),
    ]

    LANGUAGE_CHOICES = [
        ('English', 'English'),
        ('Deutsch', 'Deutsch'),
        ('Espanol', 'Espanol'),
    ]

    VOICE_CHOOSE = [
        ('Male', 'Male'),
        ('Female', 'Female'),
    ]

    name = models.CharField(max_length=50, blank=True, null=True)
    gender = models.CharField(max_length=150, choices=GENDER_CHOICES, blank=True, null=True)
    avatar = models.URLField(blank=True, null=True)
    nowlii_name = models.CharField(max_length=50, choices=NOWLII_NAME_CHOICES, blank=True, null=True)
    custom_nowlii_name = models.CharField(max_length=50, blank=True, null=True)
    language = models.CharField(max_length=50, choices=LANGUAGE_CHOICES, default='English', blank=True, null=True)
    voice = models.CharField(max_length=50, choices=VOICE_CHOOSE, default='Male', blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.custom_nowlii_name:
            self.nowlii_name = self.custom_nowlii_name
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
