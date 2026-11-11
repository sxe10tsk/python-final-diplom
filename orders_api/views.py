from django.db import transaction
from django.db.migrations import serializer
from rest_framework import generics, status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from cart.models import Cart
from catalog.models import Shop
from users.models import Contact
from .models import Order, OrderItem
from .serializers import OrderSerializer, ShopOrderSerializer
from .emails import send_order_confirmation, send_order_to_warehouse, send_order_status_change
from users.permissions import IsShopOwner


class OrderViewSet(viewsets.GenericViewSet):
	serializer_class = OrderSerializer
	permission_classes = [IsAuthenticated]

	def get_queryset(self):
		return Order.objects.filter(user=self.request.user).prefetch_related(
			'items__product_info__product',
			'items__shop',
		)
	def list(self,request):
		orders = self.get_queryset()
		serializer = OrderSerializer(orders, many=True, context={'request': request})
		return Response(serializer.data)
	def retrieve(self, request, pk=None):
		order = self.get_object()
		serializer = OrderSerializer(order, context={'request': request})
		return Response(serializer.data)
	def create(self, request):
		contact_id = request.data.get('contact')
		if not contact_id:
			return Response({'contact': ['Укажите адрес доставки']}, status=status.HTTP_400_BAD_REQUEST)
		try:
			contact = Contact.objects.get(pk=contact_id, user=request.user)
		except Contact.DoesNotExist:
			return Response({'contact': ['Контакт не найден']}, status=status.HTTP_400_BAD_REQUEST)
		try:
			cart = Cart.objects.get(user=request.user)
		except Cart.DoesNotExist:
			return Response({'detail': 'Корзина пуста'}, status=status.HTTP_400_BAD_REQUEST)

		items = cart.items.select_related('product_info__product', 'product_info__shop').all()

		if not items:
			return Response({'detail': 'Корзина пуста'}, status=status.HTTP_400_BAD_REQUEST)

		#Проверяем статус магазина и остаток товара
		for item in items:
			pi = item.product_info
			if not pi.shop.is_open:
				return Response(
					{'detail': f'Магазин «{pi.shop.name}» не принимает заказы'},
				                status=status.HTTP_400_BAD_REQUEST
				)
			if pi.quantity < item.quantity:
				return Response(
					{'detail': f'«{pi.product.name}»: на складе только {pi.quantity} шт.'},
					status=status.HTTP_400_BAD_REQUEST
				)
		#Письма вне transaction.atomic, чтобы не откатывать заказ при ошибке отправки письма
		with transaction.atomic():
			order = Order.objects.create(user=request.user, contact=contact)
			for item in items:
				pi = item.product_info
				OrderItem.objects.create(
					order=order,
					product_info=pi,
					quantity=pi.quantity,
					price=pi.price,      #Фиксация цены на момент заказа
					shop=pi.shop,)
				pi.quantity -= item.quantity
				pi.save(update_fields=['quantity'])
			cart.items.all().delete()
		send_order_confirmation(order)
		send_order_to_warehouse(order)
		serializer = OrderSerializer(order, context={'request': request})
		return Response(serializer.data, status=status.HTTP_201_CREATED)

	@action(detail=True, methods=['patch'], url_path='status')
	def update_status(self, request, pk=None):
		order = self.get_object()
		new_status = request.data.get('status')
		if new_status not in Order.Status.values: #новый статус может быть только из существующего списка
			return Response({'status': ['Неверный статус']}, status=status.HTTP_400_BAD_REQUEST)
		if new_status not in (Order.Status.CANCELED, Order.Status.NEW):
			return Response({'status': ['Клиент может только отменить заказ']}, status=403)
		order.status = new_status
		order.save(update_fields=['status', 'updated_at'])
		send_order_status_change(order)
		return Response(OrderSerializer(order, context={'request': request}).data, status=status.HTTP_200_OK)


class ShopOrderViewSet(viewsets.GenericViewSet):
	permission_classes = [IsShopOwner]
	serializer_class = ShopOrderSerializer

	def get_queryset(self):
		shop = self.request.user.shop
		return (
			Order.objects
			.filter(items__shop=shop)
			.distinct()
			.prefetch_related('items__product_info__product', 'items__shop', 'contact')
			.order_by('-created_at')
		)
	def list(self,request):
		qs = self.get_queryset()
		serializer = ShopOrderSerializer(qs, many=True, context={'request': request})
		return Response(serializer.data)
	@action(detail=True, methods=['patch'], url_path='status')
	def update_status(self, request, pk=None):
		order = self.get_object()
		new_status = request.data.get('status')
		if new_status not in Order.Status.values:
			return Response({'status': ['Неверный статус']}, status=400)
		order.status = new_status
		order.save(update_fields=['status', 'updated_at'])
		send_order_status_change(order)
		return Response(ShopOrderSerializer(order, context={'request': request}).data)

class ShopStateView(APIView):
	permission_classes = [IsShopOwner]
	def post(self, request):
		is_open = request.data.get('is_open')
		if not isinstance(is_open, bool):
			return Response({'is_open: [True or False]'}, status=status.HTTP_400_BAD_REQUEST)
		shop = request.user.shop
		shop.is_open = is_open
		shop.save(update_fields=['is_open'])
		return Response({'is_open: shop.is_open'}, status=status.HTTP_200_OK)


