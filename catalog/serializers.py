from rest_framework import serializers

from .models import Category, Shop, Product, ProductInfo, ProductParameter


class CategorySerializer(serializers.ModelSerializer):
	class Meta:
		model = Category
		fields = ('id', 'name', 'parent')


class ShopSerializer(serializers.ModelSerializer):
	class Meta:
		model = Shop
		fields = ('id', 'name', 'is_open')


class ProductParameterSerializer(serializers.ModelSerializer):
	class Meta:
		model = ProductParameter
		fields = ('name', 'value')


class ProductInfoSerializer(serializers.ModelSerializer):
	shop = ShopSerializer(read_only=True) #не даем редактировать через API
	parameters = ProductParameterSerializer(many=True, read_only=True)
	class Meta:
		model = ProductInfo
		fields = (
			'id', 'shop', 'external_id', 'model',
			'quantity', 'price', 'price_rrc', 'parameters',
		)


class ProductListSerializer(serializers.ModelSerializer):
	#Кратко для списка
	category = CategorySerializer(read_only=True)

	class Meta:
		model = Product
		fields = ('id', 'name', 'category', 'image')


class ProductDetailSerializer(serializers.ModelSerializer):
	#Детализировано для одного продукта
	category = CategorySerializer(read_only=True)
	product_infos = ProductInfoSerializer(many=True, read_only=True)
	class Meta:
		model = Product
		fields = ('id', 'name', 'category', 'description', 'image', 'product_infos')

class ShopUpdateSerializer(serializers.Serializer):
	detail = serializers.CharField()
	shop = serializers.CharField()
	created = serializers.IntegerField()
	updated = serializers.IntegerField()
	skipped = serializers.IntegerField()
