from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from django.dispatch import receiver
from django.urls import reverse
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
from simple_history.models import HistoricalRecords
from import_export import resources
from simple_history import register
from django.contrib.sessions.models import Session
from django.contrib.sessions.backends.db import SessionStore
import inspect


class UserAccountManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError('User must have an email')
        if not username:
            raise ValueError('User must have a username')

        email = self.normalize_email(email)
        user = self.model(email=email, username=username)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None):
        user = self.create_user(email, username, password)
        user.is_superuser = True
        user.is_staff = True
        user.is_active = True
        user.role = UserAccount.SUPER_ADMIN
        user.save(using=self._db)
        return user




class UserAccount(AbstractBaseUser, PermissionsMixin):
    SUPER_ADMIN = 0
    NORMAL_USER = 1
    IT_STAFF = 2

    INACTIVE = 'INACTIVE'
    ACTIVE = 'ACTIVE'
    DELETED = 'DELETED'

    USER_STATUS = (
        (INACTIVE, 'Inactive'),
        (ACTIVE, 'Active'),
        (DELETED, 'Deleted')
    )

    ROLE_TYPES = (
        (SUPER_ADMIN, 'SUPER_ADMIN'),
        (NORMAL_USER, 'NORMAL_USER'),
        (IT_STAFF, 'IT_STAFF'),
    )

    role = models.IntegerField(choices=ROLE_TYPES, default=1)
    email = models.EmailField(max_length=254, unique=True)
    username = models.CharField(max_length=255, unique=True)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    branch = models.CharField(max_length=10, blank=True, null=True, default='1')
    profile_image = models.ImageField(default='profile_pics/default.png', upload_to='media/profile_pics')
    is_staff = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    status = models.CharField(max_length=50, choices=USER_STATUS, default=ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    history = HistoricalRecords()
    objects = UserAccountManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def get_full_name(self):
        return f"{self.full_name}"
    
    def save(self, *args, **kwargs):
        if self.email and not self.profile_image:
            email_parts = self.email.split('@')
            if len(email_parts) == 2:
                email_prefix = email_parts[0]
            else:
                email_prefix = "default" 

            filename = f"profile_pics/{email_prefix}.png"

            self.profile_image.name = filename
        elif not self.profile_image:
            self.profile_image.name = 'profile_pics/default.png'

        super(UserAccount, self).save(*args, **kwargs)
        
        
    class Meta:
        verbose_name = "USER ACCOUNT"
        verbose_name_plural = "USER ACCOUNTS"
        
        
    # Override related names to avoid clashes
    groups = models.ManyToManyField(
        Group,
        related_name='useraccount_set',
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='useraccount_set',
        blank=True,
    )
        