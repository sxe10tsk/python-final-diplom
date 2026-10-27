import yaml
import hashlib
from django.contrib.auth import get_user_model

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction


from catalog.models import Product, Shop, Category, ProductInfo, ProductParameter

class Command(BaseCommand):
	help = 'Loads goods from yaml file'
	def add_arguments(self, parser):
		parser.add_argument('file', type=str)

	def handle(self, *args, **options):
		file_path = options['file']

		try:
			with open(file_path, encoding='utf-8') as file:
				data = yaml.safe_load(file)
		except FileNotFoundError:
			raise CommandError(f'File {file_path} not found')
		except yaml.YAMLError as exc:
			raise CommandError(str(exc))
		if not data or 'shop' not in data:
			raise CommandError('Shop not found')
		with transaction.atomic():
			User = get_user_model()
			shop_name = data['shop']
			slug = hashlib.md5(shop_name.encode('utf-8')).hexdigest()[:8]
			shop_user, _ = User.objects.get_or_create(
				email=f'shop-{slug}@example.com',
				defaults={
					'user_type': User.UserType.SHOP,
					'company': shop_name,
					'is_active': True,
					}
			)
			shop, _ = Shop.objects.get_or_create(
				name=shop_name,
				defaults={
					'user': shop_user,
				}
			)
			self.stdout.write(self.style.SUCCESS(f'Shop {shop_name} created'))

			categories = {}
			for cat in data.get('categories', []):
				category, _ = Category.objects.get_or_create(
					name=cat['name'],
					parent=None,
				)
				categories[cat['id']] = category
			self.stdout.write(self.style.SUCCESS(f'Amount of categories {len(categories)} created'))

			goods = data.get('goods', [])
			created_count = 0
			updated_count = 0
			for good in goods:
				category = categories.get(good['category'])
				if category is None:
					self.stdout.write(
						self.style.WARNING(
							f'Category {good["category"]} not found'
						)
					)
					continue

				product, _ = Product.objects.get_or_create(
					name=good['name'],
					category=category,
				)

				product_info, created = ProductInfo.objects.update_or_create(
					shop=shop,
					external_id=good['id'],
					defaults={
						'product': product,
						'model': good.get('model', ''),
						'quantity': good['quantity'],
						'price': good['price'],
						'price_rrc': good['price_rrc'],
					}
				)
				if created:
					created_count += 1
				else:
					updated_count += 1

				for param_name, param_values in good.get('parameters', {}).items():
					ProductParameter.objects.update_or_create(
						product_info=product_info,
						name=param_name,
						defaults={'value': str(param_values)},
					)
			self.stdout.write(self.style.SUCCESS(
				f'Goods {created_count} created, {updated_count} updated')
			)
