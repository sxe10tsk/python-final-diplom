from django.contrib import admin
from .models import Shop, Category

@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
	list_display = ('name', 'user', 'is_open')
	list_filter = ('is_open',)
	search_fields = ('name', 'user__email')
	list_select_related = ('user',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
	list_display = ('name', 'parent')
	list_filter = ('parent',)
	search_fields = ('name',)
	list_select_related = ('parent',)
