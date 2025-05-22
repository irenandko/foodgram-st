from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Subscription


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('id', 'first_name', 'last_name', 'username', 'email',)
    list_filter = ('username', 'email')
    search_fields = ('username', 'email', 'first_name')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
    search_fields = ('user__username', 'author__username')
