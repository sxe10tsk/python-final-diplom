from django.contrib import admin
from .models import Shop, Category, Product, ProductInfo, ProductParameter

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

class ProductParameterInline(admin.TabularInline):
	model = ProductParameter
	extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
	list_display = ('name', 'category')
	list_filter = ('category',)
	search_fields = ('name',)
	list_select_related = ('category',)

@admin.register(ProductInfo)
class ProductInfoAdmin(admin.ModelAdmin):
	list_display = ('product', 'shop', 'external_id', 'quantity', 'price', 'price_rrc')
	list_filter = ('shop',)
	search_fields = ('product__name', 'shop__name', 'external_id')
	list_select_related = ('shop', 'product')
	inlines = [ProductParameterInline]

@admin.register(ProductParameter)
class ProductParameterAdmin(admin.ModelAdmin):
	list_display = ('product_info', 'name', 'value')
	list_filter = ('name',)
	search_fields = ('name', 'value', 'product_info__product__name',)
	list_select_related = ('product_info',)
