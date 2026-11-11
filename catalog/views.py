import yaml
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from django.db.models import Prefetch
from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from users.permissions import IsShopOwner
from .services import import_goods_from_data
from .models import Category, Shop, Product, ProductInfo
from .serializers import (CategorySerializer, ShopSerializer, ProductListSerializer, ProductDetailSerializer,ShopUpdateSerializer)
from users.permissions import IsShopOwner


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
	queryset = Category.objects.all()
	serializer_class = CategorySerializer
	permission_classes = [AllowAny]
	ordering = ('id',)


class ShopViewSet(viewsets.ReadOnlyModelViewSet):
	queryset = Shop.objects.all()
	serializer_class = ShopSerializer
	permission_classes = [AllowAny]
	filterset_fields = ('is_open',)
	ordering = ('id',)


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
	queryset = Product.objects.all()
	permission_classes = [AllowAny]
	filterset_fields = ('category',)
	search_fields = ('name',)
	ordering_fields = ('name',)
	ordering = ('id',)


	def get_queryset(self): # Для оптимизации чтобы избежать N + 1 запросов
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


class ShopUpdateView(APIView):
	permission_classes = [IsShopOwner]
	parser_classes = [MultiPartParser, FormParser]

	@extend_schema(
		request={
			'multipart/form-data': {
				'type': 'object',
				'properties': {'file': {'type': 'string', 'format': 'binary'}},
				'required': ['file']},
		},
		responses={200:ShopUpdateSerializer},
		description=(
			'Загрузка YAML.'
		)
	)
	def post(self, request):
		file = request.FILES.get('file')
		if not file:
			return Response({'file': ['Файл отсутствует']},status=status.HTTP_400_BAD_REQUEST)
		if not file.name.endswith(('.yaml', '.yml')):
			return Response(
				{'file':['Ожидается YAML файл, а не что попало']},
				status=status.HTTP_400_BAD_REQUEST
			)
		try:
			data = yaml.safe_load(file.read().decode('utf-8'))
		except yaml.YAMLError as exc:
			return Response({'file': [f'Ошибка парсинга {exc}']},status=status.HTTP_400_BAD_REQUEST)
		except UnicodeDecodeError:
			return Response({'file': ['Необходим стандарт UTF-8']},status=status.HTTP_400_BAD_REQUEST)
		try:
			result = import_goods_from_data(data, shop=request.user.shop)
		except ValueError as e:
			return Response({'detail': str(e)},status=status.HTTP_400_BAD_REQUEST)
		return Response({
			'detail': 'Импорт успешен',
			'shop': result['shop'],
			'created': result['created_count'],
			'updated': result['updated_count'],
			'skipped': result['skipped_count'],
		},status=status.HTTP_200_OK)

