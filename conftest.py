import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

from catalog.models import Category, Shop, Product, ProductInfo
from users.models import Contact

@pytest.fixture
def api_client():
    return APIClient()

User = get_user_model()

@pytest.fixture
def user(db):
    return User.objects.create_user(
        email='client@example.com',
        password='qwerty12345',
        is_active=True
    )

@pytest.fixture
def auth_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client

@pytest.fixture
def shop_user(db):
    return User.objects.create_user(
        email='shop@example.com',
        password='Pass123!',
        user_type='shop',
        is_active=True,
    )

@pytest.fixture
def shop(db, shop_user):
    return Shop.objects.create(name='Test Shop', user=shop_user)

@pytest.fixture
def category(db):
    return Category.objects.create(name='Test Category')

@pytest.fixture
def product(db, category):
    return Product.objects.create(name='Test Product', category=category)

@pytest.fixture
def product_info(db, product, shop):
    return ProductInfo.objects.create(
        product=product,
        shop=shop,
        external_id='1',
        quantity=100,
        price=200,
        price_rrc=222,
    )

@pytest.fixture
def contact(db, user):
    return Contact.objects.create(
        user=user,
        city='test city',
        street='test street',
        house = '1',
        phone='+7123456789',
    )