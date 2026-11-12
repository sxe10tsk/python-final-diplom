from django.conf import settings
from django.db import models

from catalog.models import ProductInfo, Shop

class Order(models.Model):
	"""
    Заказ клиента. Создаётся из корзины (POST /order)
    Статус меняется через PATCH /order/<id>/status/
    """
	class Status(models.TextChoices):
		"""
	        Статусы заказа.
	        Обращение: Order.Status.NEW, Order.Status.values (список значений),
	        Order.Status.choices (список пар (value, label)).
	        """
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
		'users.Contact',
		on_delete=models.PROTECT, #Защищаем контакт от удаления если на него ссылается заказ
		related_name='orders',
		verbose_name='Адрес доставки'
	)
	status = models.CharField(
		'Статус заказа',
		max_length=20,
		choices=Status.choices,
		default=Status.NEW, #по умолчанию NEW для только что оформленного
	)
	created_at = models.DateTimeField('Заказ создан', auto_now_add=True)
	updated_at = models.DateTimeField('Заказ обновлен', auto_now=True)

	class Meta:
		verbose_name = 'Заказ'
		verbose_name_plural = 'Заказы'
		ordering = ('-created_at',) #Новые заказы первыми

	def __str__(self):
		return f' Заказ {self.pk} ({self.user.email})'

	@property
	def total_sum(self): #Итоговая стоимость заказа по всем позициям
		return sum(item.total for item in self.items.all())


class OrderItem(models.Model):
	"""
	Для фиксации цены и остатка на момент заказа
	"""
	order = models.ForeignKey(
		Order,
		related_name='items',
		on_delete=models.CASCADE,
		verbose_name='Заказ',
	)
	product_info = models.ForeignKey(
		ProductInfo,
		related_name='order_items',
		on_delete=models.PROTECT, #Не удаляем предложение если оно в заказе
		verbose_name='Предложение',
	)
	shop = models.ForeignKey(
		Shop,
		related_name='order_items',
		on_delete=models.PROTECT,
		verbose_name='Магазин'
	)
	#фиксация магазина на момент заказа

	quantity = models.PositiveIntegerField('количество')
	price = models.DecimalField('Цена на момент заказа', max_digits=10, decimal_places=2)
	#Фиксация цены на момент заказа

	class Meta:
		verbose_name = 'Позиции заказа'

	def __str__(self):
		return f'{self.product_info.product.name} × {self.quantity}'

	@property
	def total(self):
		return self.price * self.quantity