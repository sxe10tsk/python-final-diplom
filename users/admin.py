from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, Contact

@admin.register(User)
class UserAdmin(BaseUserAdmin):
	ordering = ['email']
	list_display = ('email', 'first_name', 'last_name', 'user_type', 'is_active', 'is_staff')
	list_filter = ('user_type', 'is_active', 'is_staff')
	search_fields = ('email', 'first_name', 'last_name', 'company')
	fieldsets = (
	(None, {'fields': ('email', 'password')}),
	('Данные пользователя', {'fields': ('first_name', 'last_name', 'company', 'user_type')}),
	('Права доступа', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
	)
	add_fieldsets = (
		(None, {
			'classes': ('wide',),
			'fields': ('email', 'password1', 'password2', 'user_type', 'is_active', 'is_staff'),
		}),
	)

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
	list_display = ('user', 'city', 'street', 'house', 'apartment', 'phone', 'is_default_adress')
	list_filter = ('city', 'is_default_adress')
	search_fields = ('user__email', 'city', 'street', 'phone')
	list_select_related = ('user',)
