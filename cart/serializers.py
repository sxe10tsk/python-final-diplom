from rest_framework import serializers

from catalog.models import ProductInfo
from catalog.serializers import ProductInfoSerializer
from .models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
	product_info = ProductInfoSerializer(read_only=True)
	product_info_id = serializers.PrimaryKeyRelatedField(
		queryset=ProductInfo.objects.all(),
		source='product_info',
		write_only=True,
	)
	total = serializers.SerializerMethodField()

	class Meta:
		model = CartItem
		fields = ('id', 'product_info_id', 'product_info', 'quantity', 'total')

	def get_total(self, obj):
		return obj.product_info.price * obj.quantity
	def validate(self, attrs):
		product_info = attrs.get('product_info') or (self.instance.product_info if self.instance else None)
		quantity = attrs.get('quantity', self.instance.quantity if self.instance else 1)
		if product_info is None:
			raise serializers.ValidationError('Product info cannot be None')
		if not product_info.shop.is_open:
			raise serializers.ValidationError('Магазин не принимает заказы')
		if product_info.quantity < quantity:
			raise serializers.ValidationError('Недостаточный остаток на складе')
		if quantity < 1:
			raise serializers.ValidationError('Невозможно добавить меньше 1 товара')

		return attrs


class CartSerializer(serializers.ModelSerializer):
	items = CartItemSerializer(read_only=True, many=True)
	total_sum = serializers.SerializerMethodField()
	total_items = serializers.SerializerMethodField()

	class Meta:
		model = Cart
		fields = ('id', 'items', 'total_sum', 'total_items')

	def get_total_sum(self, obj):
		return sum(item.product_info.price * item.quantity for item in obj.items.all())
	def get_total_items(self, obj):
		return sum(item.quantity for item in obj.items.all())

