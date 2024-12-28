from django.contrib.auth.base_user import BaseUserManager

class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifier.
    """
    def create_user(self, email, password=None, ip_address=None, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError('The Email field must be set')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        
        if password:
            user.set_password(password)
        
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_admin', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()

        return user


from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone 
from utils.constraint_fields import ContentTypeRestrictedFileField

class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model where email is the unique identifier
    and optional profile fields.
    """
    name = models.CharField(max_length=30, null=True, blank=True)
    email = models.EmailField(unique=True, null=False, blank=False)
    dp = ContentTypeRestrictedFileField(upload_to='dp/', content_types=['image/png', 'image/jpeg'], 
                                        max_upload_size=5242880,  null=True, blank=True)  # Profile picture
    ip_address = models.GenericIPAddressField(null=True, blank=True)  # User's IP address
    
    # User flags
    is_admin = models.BooleanField(default=False)  # Admin indicator
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    date_joined = models.DateTimeField(default=timezone.now)

    # Custom Manager
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'  # The unique identifier for the user is the email

    def __str__(self):
        return f'{self.email}'
    
    def clean(self):
        """
        Clean method to handle custom validation
        """
        cleaned = super().clean()
        # Ensure name is populated from email if not provided
        if not self.name and self.email:
            name_part = self.email.split('@')[0].replace('.', ' ').capitalize()
            self.name = name_part[:30]  # Ensure name is within 30 chars
        return cleaned

    def save(self, *args, **kwargs):
        """
        Custom save method to ensure correct flag logic
        """
        # Only a staff user can become an admin
        if self.is_admin:
            self.is_staff = True

        if not self.is_staff:
            self.is_admin = False

        # Admin and superuser settings
        if self.is_superuser:
            self.is_staff = True
            self.is_admin = True
        
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
