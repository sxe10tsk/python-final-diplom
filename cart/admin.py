from django.contrib import admin
from .models import Cart, CartItem

class CartItemInLine(admin.TabularInline):
	model = CartItem
	extra = 0

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
	list_display = ('id', 'user', 'created_at')
	search_fields = ('user__email',)
	list_search_related = ('user',)
	inlines = [CartItemInLine]

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
	list_display = ('cart', 'product_info', 'quantity')
	search_fields = ('cart__user__email', 'product__info__product_name')
	list_search_related = ('cart', 'product_info')
	