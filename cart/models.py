from django.conf import settings
from django.db import models

from catalog.models import ProductInfo


class Cart(models.Model):
    """
    Корзина пользователя. Один пользователь - одна корзина
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name='User',
    )

    created_at = models.DateTimeField('Создана', auto_now_add=True)

    class Meta:
        verbose_name = 'Корзина'

    def __str__(self):
        return f'Корзина {self.user.email}'

    @property
    def total_sum(self): #общая стоимость корзины
        return sum(item.product_info.price * item.quantity for item in self.items.all())

    @property
    def total_items(self): #Количество единиц товара в корзине
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    """
    ПОзиции товара в корзине и их количество. Одна позиция на товар
    """
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Корзина',
    )
    product_info = models.ForeignKey(
        ProductInfo,
        on_delete=models.CASCADE,
        related_name='cart_items',
        verbose_name='Предложение'
    )
    quantity = models.PositiveIntegerField('Количество', default=1)

    class Meta:
        verbose_name = 'Позиция'
        unique_together = ('cart', 'product_info') #Нельзя дважды добавить один product_info в корзину
                                                   #вместо этого увеличиваем quantity

    def __str__(self):
        return f'{self.product_info.product.name} × {self.quantity}'