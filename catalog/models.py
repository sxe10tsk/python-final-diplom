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


