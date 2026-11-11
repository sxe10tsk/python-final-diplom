Backend-сервис заказа товаров

Клиент может выбрать товары из каталога, добавить их в
корзину, оформить заказ, указав адресс доставки.
Поставщик может видеть и управлять заказами из своего
магазина. Через email отправляются письма: Подтверждение регистрации,
Заказ, Накладная, Смена статуса заказа
___
Для запуска:

1) Клонировать репозиторий 
```bash
git clone https://github.com/sxe10tsk/python-final-diplom.git
cd python-final-diplom
```

2) Создать виртуальное окружение
```bash
python3 -m venv env
source env/bin/activate
```

3) Установить зависимости
```bash
pip install -r requirements.txt
```

4) Применить миграции
```bash
python manage.py migrate
```

5) создать суперпользователя
```bash
python manage.py createsuperuser
```
Необходимо ввести EMAIL(не USERNAME) и пароль ( не менее 8 символов, буквы и цифры)

6) Импорт товаров из YAML файла
Скопировать YAML файл в папку 'data/' (например, `data/shop1.yaml`)

```bash
python manage.py load_goods "data/shop1.yaml"
```

7) Запустите сервер

```bash
python manage.py runserver
```

admin: `http://127.0.0.1:8000/admin/`
API: `http://127.0.0.1:8000/api/v1/`
Swagger: `http://127.0.0.1:8000/api/schema/swagger-ui/`

8) Тесты
```bash
pytest
```
Тесты покрывают: Регистрацию, Логин, Каталог, Корзину, Заказы, изоляцию, email.

Запуск по файлу / тесту:

```bash
pytest users/tests.py
pytest orders_api/tests.py::test_full_order -v
pytest -k "order or cart"
```
___
API
1) метод POST:
-    `/api/v1/user/register` Регистрация писмо с подтверждением в терминал`/api/v1/user/login` | Логин
-    `/api/v1/user/login` Логин
-    `/api/v1/shop/state` Изменение статуса активности магазина
-    `/api/v1/shop/update` Загрузка YAML-каталога
-    `/api/v1/user/contact` Контакты (адрес)
-    `/api/v1/cart/` Корзина
-    `/api/v1/order/` Оформить заказ `{"contact": id}`
2) метод GET
- `/api/v1/user/details` Профиль
- `/api/v1/user/contact` Контакты (адресс)
- `/api/v1/products/` Каталог /фильтрация(`?category=`, `?search=`, `?page=`)
- `/api/v1/products/<id>/` ПОдробно о товаре
- `/api/v1/cart/` Корзина
- `/api/v1/order/` Список заказов
- `/api/v1/shop/orders/` Список заказов поставщика
3) Метод PATCH
- `/api/v1/user/details` Профиль
- `/api/v1/order/<id>/status/` Смена статуса щзаказа
- 

___
Структура проекта:
1) `users/` — User, Contact, авторизация
2) `catalog/` — Shop, Category, Product, ProductInfo, ProductParameter; `load_goods`
3) `cart/` — Cart, CartItem
4) `orders_api/` — Order, OrderItem, emails
5) `orders/` — settings, urls
6) `api/` — маршрутизация
___
Используемые фреймворки и пакеты

- Django 5.2, Django REST Framework — backend + API
- drf-spectacular — Swagger UI
- django-filter — для фильтрации
- PyYAML — для импорта каталогов YAML от поставщиков
- Pillow — изображения
- pytest, pytest-django — тесты
- SQLite
___
Ключевые решения:
1) Пользовательская модель User без username с логином по email
2) Product и ProductInfo: Одинаковый товар с одними и теми же характеристиками может
отличаться в магазинах по стоимости и остатку
3) TokenAuthentication авторизация, встроенная в DRF
4) Отдельная таблица для ProductParameter: простота фильтрации, валидации, индексации, контроля уникальности
5) unique_together% ограничение БД (составной уникальный ключ), при добавлении в корзину того же товара,
увеличивается количество, а не дублируется товар, так же помогает избежать дублирования товаров при импорте
6) transaction.atomic() в случае появления ошибки в ходе выполнения скрипта откатывается к исходному состоянию
7) get_queryset фильтрация по request.user для изоляции, пользователь видит только свои корзину, заказ, контакты
___
Известные ограничения:
1) Celery не подключен
2) Для разработки дипломного проетка использован SQLite
