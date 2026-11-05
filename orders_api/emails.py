from django.conf import settings
from django.core.mail import send_mail, message


#Преобразование позиции в текс для письма
def _format_items(items):
	lines = []
	for item in items:
		lines.append(
			f'{item.product_info.product.name} x {item.quantity}  '
			f'Стоимость {item.total} рублей  '
			f'Магазин: {item.shop.name}  '
		)
	return '\n'.join(lines)

#Отправка уведомления клиенту
def send_order_confirmation(order):
	subject = f'Заказ №{order.pk} успешно оформлен'
	items_text = _format_items(order.items.select_related('product_info__product', 'shop'))
	message = (
		f'Здравствуйте!\n\n'
		f'Заказ №{order.pk} успешно оформлен\n\n'
		f'Состав заказа: {items_text} \n\n'
		f'Итого к оплате: {order.total_sum} рублей \n\n'
		f'Адресс доставки: {order.contact}\n\n'
		f'Ваш контактный телефон: {order.contact.phone}\n\n'
		f'Статус вашего заказа: {order.get_status_display()}\n\n'
	)
	send_mail(
		subject=subject,
		message=message,
		from_email=settings.DEFAULT_FROM_EMAIL,
		recipient_list=[order.user.email],
		fail_silently=False,
	)

#Отправка письма-накладной на склад
def send_order_to_warehouse(order):
	subject = f'Накладная к заказу {order.pk}'
	items_text = _format_items(order.items.select_related('product_info__product', 'shop'))
	message = (
		f'Заказ № {order.pk} к сборке\n\n'
		f'Клиент: {order.user.email}\n'
		f'Адрес доставки: {order.contact}\n'
		f'Контактный телефон: {order.contact.phone}\n'
		f'Позиции к сборке: {items_text} \n'
		f'Сумма к оплате: {order.total_sum} рублей\n\n'
	)
	send_mail(
		subject=subject,
		message=message,
		from_email=settings.DEFAULT_FROM_EMAIL,
		recipient_list=[settings.DEFAULT_FROM_EMAIL],
		fail_silently=False,
	)

def send_order_status_change(order):
	#Уведомление об изменении статуса заказа
	subject = f'Статус вашего заказа №{order.pk} изменен'
	message = (
		f'Здравствуйте!\n\n'
		f'Статус вашего заказа №{order.pk} изменен на {order.get_status_display()}\n\n'
		f'Состав заказа:\n{_format_items(order.items.select_related("product_info__product", "shop"))}\n\n'
		f'Итого: {order.total_sum} рублей\n\n'
	)
	send_mail(
		subject=subject,
		message=message,
		from_email=settings.DEFAULT_FROM_EMAIL,
		recipient_list=[order.user.email],
		fail_silently=False,
	)
