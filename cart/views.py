from django.db.migrations import serializer
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer


class CartViewSet(viewsets.GenericViewSet):
	permission_classes = [IsAuthenticated]
	serializer_class = CartSerializer

	def get_queryset(self):
		return Cart.objects.filter(user=self.request.user).prefetch_related(
			'items__product_info__shop',
			'items__product_info__parameters',
		)
	def _get_cart(self):
		cart, _ = Cart.objects.get_or_create(user=self.request.user)
		return cart
	def list(self, request):
		cart = self._get_cart()
		serializer = CartSerializer(cart, context={'request': request})
		return Response(serializer.data)
	def create(self, request):
		cart = self._get_cart()
		serializer = CartItemSerializer(data=request.data, context={'request': request})
		serializer.is_valid(raise_exception=True)
		product_info = serializer.validated_data['product_info']
		quantity = serializer.validated_data.get('quantity', 1)

		item, created = CartItem.objects.get_or_create(
			cart=cart,
			product_info=product_info,
			defaults={'quantity': quantity}
		)
		if not created:
			item.quantity += quantity
			item.full_clean()
			item.save()

		return Response(
			CartSerializer(cart, context={'request': request}).data,
			status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
		)

	@action(detail=True, methods=['patch', 'delete'])
	def item(self, request, pk=None):
		cart = self._get_cart()
		try:
			item = cart.items.get(pk=pk)
		except CartItem.DoesNotExist:
			return Response({'detail': 'Позиция не найдена'}, status=status.HTTP_404_NOT_FOUND)

		if request.method == 'DELETE':
			item.delete()
			return Response(status=status.HTTP_204_NO_CONTENT)
		serializer = CartItemSerializer(item, data=request.data, partial=True,
		                                context={'request': request})
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return Response(CartSerializer(cart, context={'request': request}).data)

	@action(detail=False, methods=['delete'])
	def clear(self, request):
		cart = self._get_cart()
		cart.items.all().delete()
		return Response(status=status.HTTP_204_NO_CONTENT)


