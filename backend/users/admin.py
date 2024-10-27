from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from rest_framework.authtoken.models import TokenProxy

from .models import Subscriber, User


@admin.register(User)
class UsersAdmin(UserAdmin):
    """User admin site."""

    list_display = (
        'id',
        'full_name',
        'username',
        'email',
        'is_staff'
    )
    search_fields = (
        'username',
        'email'
    )
    search_help_text = 'Поиск по `username` и `email`'
    list_display_links = (
        'id',
        'username',
        'email',
        'full_name'
    )

    @admin.display(description='Имя фамилия')
    def full_name(self, obj):
        """Get full name."""
        return obj.get_full_name()


admin.site.register(Subscriber)

admin.site.unregister([Group, TokenProxy])
