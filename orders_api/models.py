from django.conf import settings
from django.db import models

from catalog.models import ProductInfo, Shop

class Order(models.Model):
	class Status(models.TextChoices):
		BASKET = 'basket', 'Корзина'
		NEW = 'new', 'Новый'
		CONFIRMED = 'confirmed', 'Подтвержден'
		ASSEMBLING = 'assembling', 'Собирается'
		SENT = 'sent', 'Отправлен'
		DELIVERED = 'delivered', 'Доставлен'
		CANCELED = 'canceled', 'Отменен'

	user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name='orders',
		verbose_name='Клиент'
	)
	contact = models.ForeignKey(
		'users.contact',
		on_delete=models.PROTECT,
		related_name='orders',
		verbose_name='Адресс доставки'
	)
	status = models.CharField(
		'Статус доставки',
		max_length=20,
		choices=Status.choices,
		default=Status.NEW,
	)
	created_at = models.DateTimeField('Заказ создан', auto_now_add=True)
	updated_at = models.DateTimeField('Заказ обновлен', auto_now=True)

	class Meta:
		verbose_name = 'Заказ'
		verbose_name_plural = 'Заказы'
		ordering = ('-created_at',)

	def __str__(self):
		return f' Заказ {self.pk} ({self.user.email})'

	@property
	def total_sum(self):
		return sum(item.total for item in self.items.all())


class OrderItem(models.Model):
	order = models.ForeignKey(
		Order,
		related_name='items',
		on_delete=models.CASCADE,
		verbose_name='Заказ',
	)
	product_info = models.ForeignKey(
		ProductInfo,
		related_name='order_items',
		on_delete=models.PROTECT,
		verbose_name='Предложение',
	)
	shop = models.ForeignKey(
		Shop,
		related_name='order_items',
		on_delete=models.PROTECT,
		verbose_name='Магазин'
	)
	quantity = models.PositiveIntegerField('колиество')
	price = models.DecimalField('Цена на момент заказа', max_digits=10, decimal_places=2)

	class Meta:
		verbose_name = 'Позиции заказа'

	def __str__(self):
		return f'{self.product_info.product_name} × {self.quantity}'

	@property
	def total(self):
		return self.price * self.quantity