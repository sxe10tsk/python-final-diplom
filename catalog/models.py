from django.db import models
from django.conf import settings

class Shop(models.Model):
	name = models.CharField('Название', max_length=100)
	user = models.OneToOneField(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name='shop',
		verbose_name='Поставщик'
	)
	is_open = models.BooleanField('При ем заказов', default=True)
	filename = models.CharField('Прайс-лист', max_length=255, blank=True)

	def __str__(self):
		return self.name

class Category(models.Model):
	name = models.CharField('Наименование', max_length=100)
	parent = models.ForeignKey(
		'self',
		on_delete=models.CASCADE,
		null=True,
		blank=True,
		related_name='children',
		verbose_name= 'Родительская категория'
	)
	class Meta:
		unique_together = ('name', 'parent')

	def __str__(self):
		return self.name

class Product(models.Model):
	name = models.CharField('Наименование', max_length=255)
	category = models.ForeignKey(
		Category,
		on_delete=models.CASCADE,
		related_name='products',
		verbose_name='Категория'
	)
	description = models.TextField('Описание', blank=True)
	image = models.ImageField(
		'Изображение',
		upload_to='products/',
		blank=True,
		null=True)
	def __str__(self):
		return self.name

class ProductInfo(models.Model):
	product = models.ForeignKey(
		Product,
		on_delete=models.CASCADE,
		related_name='product_infos',
		verbose_name='Товар'
	)
	shop = models.ForeignKey(
		Shop,
		on_delete=models.CASCADE,
		related_name='product_infos',
		verbose_name='Поставщик'
	)
	external_id = models.PositiveIntegerField('Артикул у поставщика')
	model = models.CharField('Модель', max_length=255, blank=True)
	quantity = models.PositiveIntegerField('Количество на остатке', default=0)
	price = models.DecimalField('Стоимость', max_digits=10, decimal_places=2)
	price_rrc = models.DecimalField(
		'Рекомендованная розничная цена',
		max_digits=10,
		decimal_places=2
	)

	class Meta:
		unique_together = ('shop', 'external_id')

	def __str__(self):
		return f'{self.product.name} - {self.shop.name} {self.price} руб.'

class ProductParameter(models.Model):
	product_info = models.ForeignKey(
		ProductInfo,
		on_delete=models.CASCADE,
		related_name='parameters',
		verbose_name='товар в наличии'
	)
	name = models.CharField('Характеристика', max_length=255)
	value = models.CharField('Значение', max_length=255)

	class Meta:
		unique_together = ('product_info', 'name')

	def __str__(self):
		return f'{self.name} - {self.value}'


