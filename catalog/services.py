import hashlib
from django.db import transaction

from catalog.models import Shop, Category, Product, ProductInfo, ProductParameter
from users.models import User


#В случае использования менеджмент команды load_goods, если SHOP был создан без реального пользователя
def _make_shop_email(shop_name: str) -> str:
	slug = hashlib.md5(shop_name.encode('utf-8')).hexdigest()[:8]
	return f'shop-{slug}@example.com'


def import_goods_from_data(data: dict, shop: Shop | None = None) -> dict:
	"""
	Импортирует товары из словаря YAML в БД
	"""
	if not data:
		raise ValueError('No data provided')
	if shop is None and 'shop' not in data:
		raise ValueError('No shop provided')
	if 'goods' not in data:
		raise ValueError('No goods provided')
	#Валидируем до осуществления транзщакции

	created_count = 0
	updated_count = 0
	skipped_count = 0

	with transaction.atomic(): #Откат при любой ошибке, не допустим частичного импорта

		if shop is None: # management-команда: создаём/находим магазин по имени.
			shop_name = data['shop']
			shop_user, _ = User.objects.get_or_create(
				email=_make_shop_email(shop_name),
				defaults={'user_type': User.UserType.SHOP, 'company': shop_name, 'is_active': True,},
			)
			shop, _ = Shop.objects.get_or_create(
				name=shop_name,
				defaults={'user': shop_user},
			)
			# API-режим (shop передан): магазин уже есть, ничего не создаём

		categories = {}
		for cat in data.get('categories', []):  # ← data, не categories
			category, _ = Category.objects.get_or_create(name=cat['name'], parent=None)
			categories[cat['id']] = category

		for good in data.get('goods', []):
			category = categories.get(good['category'])
			if category is None:
				skipped_count += 1
				continue

			product, _ = Product.objects.get_or_create(name=good['name'], category=category)
			product_info, created = ProductInfo.objects.update_or_create(
				shop=shop,
				external_id = good['id'],
				defaults={
					'product': product,
					'model': good.get('model', ''),
					'price': good['price'],
					'price_rrc': good['price_rrc'],
					'quantity': good.get('quantity', 0),
				}
			)
			if created:
				created_count += 1
			else:
				updated_count += 1

			for param_name, param_value in good.get('parameters', {}).items():
				ProductParameter.objects.update_or_create(
					product_info=product_info,
					name=param_name,
					defaults={
						'value': str(param_value),
					}
				)
	return {
		'created_count': created_count,
		'updated_count': updated_count,
		'skipped_count': skipped_count,
		'shop': shop.name,
	}


