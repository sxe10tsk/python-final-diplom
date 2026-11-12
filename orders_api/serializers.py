from rest_framework import serializers

from users.models import Contact
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
	product_name = serializers.CharField(
		source='product_info.product.name',
		read_only=True
	)
	shop_name = serializers.CharField(
		source='shop.name',
		read_only=True
	)
	total = serializers.DecimalField(
		max_digits=12,
		decimal_places=2,
		read_only=True
	)

	class Meta:
		model = OrderItem
		fields = (
			'id',
			'product_name',
			'product_info',
			'shop',
			'shop_name',
			'quantity',
			'price',
			'total',
		)
		read_only_fields = ('id', 'price', 'total')


class OrderSerializer(serializers.ModelSerializer):
	items = OrderItemSerializer(many=True, read_only=True)
	total_sum = serializers.DecimalField(max_digits=12, decimal_places=2,read_only=True)
	contact = serializers.PrimaryKeyRelatedField(queryset=Contact.objects.none())
	status_display = serializers.CharField(source='get_status_display', read_only=True)

	class Meta:
		model = Order
		fields = (
			'id', 'contact', 'status', 'status_display',
            'created_at', 'updated_at', 'items', 'total_sum',
		)

		read_only_fields = ('id', 'created_at', 'updated_at', 'total_sum', 'status')

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		request = self.context.get('request')
		if request and request.user.is_authenticated:
			self.fields['contact'].queryset = Contact.objects.filter(user=request.user)


class ShopOrderItemSerializer(serializers.ModelSerializer):
	product_name = serializers.CharField(
		source='product_info.product.name',
		read_only=True
	)
	total = serializers.DecimalField(max_digits=12, decimal_places=2,read_only=True)
	class Meta:
		model = OrderItem
		fields = (
			'id',
			'product_name',
			'product_info',
			'quantity',
			'price',
			'total',
		)
		read_only_fields = (
			'id',
			'product_name',
			'product_info',
			'quantity',
			'price',
			'total',
		)


class ShopOrderSerializer(serializers.ModelSerializer):
	items = serializers.SerializerMethodField()
	total_sum = serializers.SerializerMethodField()
	contact = serializers.SerializerMethodField()
	status_display = serializers.CharField(source='get_status_display', read_only=True)

	class Meta:
		model = Order
		fields = (
			'id',
			'contact',
			'status',
			'status_display',
			'created_at',
			'items',
			'total_sum',
		)
		read_only_fields = fields

	def get_items(self, obj):
		shop = self.context['request'].user.shop
		items = obj.items.filter(shop=shop)
		return ShopOrderItemSerializer(items, many=True).data

	def get_total_sum(self, obj):
		shop = self.context['request'].user.shop
		return sum(item.total for item in obj.items.filter(shop=shop))

	def get_contact(self, obj):
		c = obj.contact
		return {
			'city': c.city,
			'street': c.street,
			'house': c.house,
			'building': c.building,
			'apartment': c.apartment,
			'phone': c.phone,
		}
