## Backend-сервис заказа товаров

Клиент может выбрать товары из каталога, добавить их в
корзину, оформить заказ, указав адрес доставки.
Поставщик может видеть и управлять заказами из своего
магазина. Через email отправляются письма: Подтверждение регистрации,
Заказ, Накладная, Смена статуса заказа
___
## Для запуска:

1) **Клонировать репозиторий**
```bash
git clone https://github.com/sxe10tsk/python-final-diplom.git
cd python-final-diplom
```

2) **Создать виртуальное окружение**
```bash
python3 -m venv env
source env/bin/activate
```

3) **Установить зависимости**
```bash
pip install -r requirements.txt
```

4) **Применить миграции**
```bash
python manage.py migrate
```

5) **Создать суперпользователя**
```bash
python manage.py createsuperuser
```
Необходимо ввести EMAIL(не USERNAME) и пароль (не менее 8 символов, буквы и цифры)

6) **Импорт товаров из YAML файла**
Скопировать YAML файл в папку 'data/' (например, `data/shop1.yaml`)

```bash
python manage.py load_goods "data/shop1.yaml"
```

7) **Запустите сервер**

```bash
python manage.py runserver
```

admin: `http://127.0.0.1:8000/admin/`
API: `http://127.0.0.1:8000/api/v1/`
Swagger: `http://127.0.0.1:8000/api/schema/swagger-ui/`

8) **Тесты**
```bash
pytest
```
21 тест покрывает: Регистрацию, Логин, Каталог, Корзину, Заказы, изоляцию, email.

**Запуск по файлу / тесту**:

```bash
pytest users/tests.py
pytest orders_api/tests.py::test_full_order -v
pytest -k "order or cart"
```
___
## API:

**Аутентификация:** `Authorization: Token <key>` (токен из `POST /user/login`).

| Метод | URL | Что |
|---|---|---|
| POST | `/api/v1/user/register` | Регистрация (письмо с подтверждением в терминал) |
| POST | `/api/v1/user/register/confirm/<uidb64>/<token>` | Подтверждение email |
| POST | `/api/v1/user/login` | Логин → токен |
| POST | `/api/v1/user/logout` | Logout (удалить токен) |
| GET/PATCH | `/api/v1/user/details` | Профиль |
| POST | `/api/v1/user/password-reset` | Запрос сброса пароля |
| POST | `/api/v1/user/password-reset/confirm/<uidb64>/<token>` | Подтверждение сброса |
| GET/POST | `/api/v1/user/contact` | Контакты (список / создание) |
| GET/PATCH/DELETE | `/api/v1/user/contact/<id>` | Контакт (детали / редактирование / удаление) |
| GET | `/api/v1/products/` | Каталог (`?category=`, `?search=`, `?page=`) |
| GET | `/api/v1/products/<id>/` | Детали товара (предложения, характеристики) |
| GET | `/api/v1/categories/` | Категории |
| GET | `/api/v1/shops/` | Магазины (`?is_open=true`) |
| GET/POST | `/api/v1/cart/` | Корзина (список / добавление) |
| PATCH/DELETE | `/api/v1/cart/<id>/item/` | Позиция корзины (изменить / удалить) |
| DELETE | `/api/v1/cart/clear/` | Очистить корзину |
| POST | `/api/v1/order/` | Оформить заказ (`{"contact": id}`) |
| GET | `/api/v1/order/` | Список заказов |
| GET | `/api/v1/order/<id>/` | Детали заказа |
| PATCH | `/api/v1/order/<id>/status/` | Смена статуса (клиент — только `canceled`) |
| GET | `/api/v1/shop/orders/` | Заказы магазина (поставщик) |
| PATCH | `/api/v1/shop/orders/<id>/status/` | Смена статуса (поставщик) |
| POST | `/api/v1/shop/state` | Вкл/выкл приём заказов (`{"is_open": true/false}`) |
| POST | `/api/v1/shop/update` | Загрузка YAML-прайса (multipart/form-data, поле `file`) |

## Структура проекта:
1) `users/` — User, Contact, авторизация
2) `catalog/` — Shop, Category, Product, ProductInfo, ProductParameter; `load_goods`
3) `cart/` — Cart, CartItem
4) `orders_api/` — Order, OrderItem, emails
5) `orders/` — settings, urls
6) `api/` — маршрутизация
___
## Используемые фреймворки и пакеты:

- Django 5.2, Django REST Framework — backend + API
- drf-spectacular — Swagger UI
- django-filter — для фильтрации
- PyYAML — для импорта каталогов YAML от поставщиков
- Pillow — изображения
- pytest, pytest-django — тесты
- SQLite
___
## Ключевые решения:
1) Пользовательская модель User без username с логином по email
2) Product и ProductInfo: Одинаковый товар с одними и теми же характеристиками может
отличаться в магазинах по стоимости и остатку
3) TokenAuthentication авторизация, встроенная в DRF
4) Отдельная таблица для ProductParameter: простота фильтрации, валидации, индексации, контроля уникальности
5) unique_together ограничение БД (составной уникальный ключ), при добавлении в корзину того же товара,
увеличивается количество, а не дублируется товар, так же помогает избежать дублирования товаров при импорте
6) transaction.atomic() в случае появления ошибки в ходе выполнения скрипта откатывается к исходному состоянию
7) get_queryset фильтрация по request.user для изоляции, пользователь видит только свои корзину, заказ, контакты
___
## Известные ограничения:
1) Celery не подключен
2) Для разработки дипломного проекта использован SQLite
