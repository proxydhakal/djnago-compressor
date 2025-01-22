from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from apps.accounts.models import UserAccount
class UserAccountAdmin(UserAdmin):
    ordering = ['email']
    list_display = ('email', 'full_name', 'role', 'is_active')

    fieldsets = (
        (None, {'fields': ('email', 'password',)}),  # Include necessary fields like 'email', 'password'
        ('Personal info', {'fields': ('full_name', 'profile_image', 'phone', 'branch')}),  # Add other personal info fields
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'role','groups', 'user_permissions')}),  # Include permissions and roles
        # Remove 'date_joined' from the fieldsets
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2','full_name', 'profile_image', 'phone','branch', 'is_active', 'is_staff', 'is_superuser', 'role'),
        }),
    )

admin.site.register(UserAccount, UserAccountAdmin)
