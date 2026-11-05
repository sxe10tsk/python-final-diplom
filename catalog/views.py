from django.db.models import Prefetch
from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from .models import Category, Shop, Product, ProductInfo
from .serializers import (CategorySerializer, ShopSerializer, ProductListSerializer, ProductDetailSerializer,)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
	queryset = Category.objects.all()
	serializer_class = CategorySerializer
	permission_classes = [AllowAny]


class ShopViewSet(viewsets.ReadOnlyModelViewSet):
	queryset = Shop.objects.all()
	serializer_class = ShopSerializer
	permission_classes = [AllowAny]
	filterset_fields = ('is_open',)


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
	queryset = Product.objects.all()
	permission_classes = [AllowAny]
	filterset_fields = ('category',)
	search_fields = ('name',)
	ordering_fields = ('name',)

	def get_queryset(self):
		qs = Product.objects.select_related('category')
		if self.action == 'retrieve':
			qs = qs.prefetch_related(
				Prefetch(
					'product_infos',
					queryset=ProductInfo.objects.select_related('shop').prefetch_related('parameters'),
				)
			)
		return qs
	def get_serializer_class(self):
		if self.action == 'retrieve':
			return ProductDetailSerializer
		return ProductListSerializer
