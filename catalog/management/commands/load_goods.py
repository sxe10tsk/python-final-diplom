import yaml
from django.core.management.base import BaseCommand, CommandError

from catalog.services import import_goods_from_data

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
		try:
			result = import_goods_from_data(data)  # shop=None → команда
		except ValueError as exc:

			raise CommandError(str(exc))
		self.stdout.write(
			self.style.SUCCESS(
				f"магазин: {result['shop']}; "
				f"создано: {result['created_count']}, обновлено: {result['updated_count']}, "
				f"пропущено: {result['skipped_count']}"
			)
		)
