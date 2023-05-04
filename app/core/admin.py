from django.contrib import admin # noqa
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from core import models

# Register your models here.


class UserAdmin(BaseUserAdmin):
    """Admin for custom user model"""
    ordering = ['id']
    list_display = ['email', 'name']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('name',)}),
        (
            'Permissions',
            {'fields': ('is_active', 'is_staff', 'is_superuser')}
        ),
        ('Important dates', {'fields': ('last_login',)})
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'name', 'is_active',
                       'is_staff', 'is_superuser')
        }),
    )


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Recepie)
admin.site.register(models.Tag)
