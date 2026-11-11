import pytest
from rest_framework import status

from catalog.models import ProductInfo

#Воспроизведение полного сценария заказа, отправка писем, списание остатка
@pytest.mark.django_db
def test_full_order(auth_client, user, contact, product_info, mailoutbox):
	auth_client.post('/api/v1/cart/', {
		'product_info_id': product_info.id,
		'quantity': 1,
	}, format='json')
	mailoutbox.clear()

	response = auth_client.post('/api/v1/order/', {'contact': contact.id,}, format='json')
	assert response.status_code == status.HTTP_201_CREATED
	order_id = response.data['id']

	assert len(mailoutbox) == 2
	recipients = [m.to[0] for m in mailoutbox]
	assert 'client@example.com' in recipients

	product_info.refresh_from_db()
	assert product_info.quantity == 99

	cart = auth_client.get('/api/v1/cart/')
	assert cart.data['items'] == []

	orders = auth_client.get('/api/v1/order/')
	assert len(orders.data) == 1
	assert orders.data[0]['id'] == order_id


@pytest.mark.django_db
def test_empty_cart_order(auth_client, contact):
	response = auth_client.post('/api/v1/order/', {'contact': contact.id}, format='json')
	assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.django_db
def test_no_contact_info(auth_client, product_info):
	auth_client.post('/api/v1/cart/', {
		'product_info_id': product_info.id,
		'quantity': 1,
	}, format='json')
	response = auth_client.post('/api/v1/order/', {}, format='json')
	assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.django_db
def test_status_change_email(auth_client, contact, product_info, mailoutbox):
	auth_client.post('/api/v1/cart/', {
		'product_info_id': product_info.id,
		'quantity': 1,
	}, format='json')
	response = auth_client.post('/api/v1/order/', {'contact': contact.id,}, format='json')
	order_id = response.data['id']
	mailoutbox.clear()
	response = auth_client.patch(
		f'/api/v1/order/{order_id}/status/',
		{'status': 'canceled'},
		format='json'
	)
	assert response.status_code == status.HTTP_200_OK
	assert response.data['status'] == 'canceled'
	assert len(mailoutbox) == 1

@pytest.mark.django_db
def test_other_user_to_see_order(auth_client, contact, product_info):
	from django.contrib.auth import get_user_model
	from rest_framework.test import APIClient
	User = get_user_model()
	auth_client.post('/api/v1/cart/', {
		'product_info_id': product_info.id,
		'quantity': 1,
	}, format='json')
	auth_client.post('/api/v1/order/', {'contact': contact.id,}, format='json')

	other = User.objects.create_user(
		email='other1@testmail.com',
		password='Pass123456789',
		is_active=True,
	)
	other_client = APIClient()
	other_client.force_authenticate(user=other)
	response = other_client.get('/api/v1/order/')
	assert len(response.data) == 0

@pytest.mark.django_db
def test_shop_change_status(auth_client, contact, product_info, shop_user, mailoutbox):
	from rest_framework.test import APIClient

	# создание заказа клиентом
	auth_client.post('/api/v1/cart/', {'product_info_id': product_info.id, 'quantity': 1}, format='json')
	response = auth_client.post('/api/v1/order/', {'contact': contact.id}, format='json')
	order_id = response.data['id']
	mailoutbox.clear()

	# изменение статуса поставщиком
	shop_client = APIClient()
	shop_client.force_authenticate(user=shop_user)
	response = shop_client.patch(
		f'/api/v1/shop/orders/{order_id}/status/',
		{'status': 'confirmed'},
		format='json',
	)
	assert response.status_code == status.HTTP_200_OK
	assert response.data['status'] == 'confirmed'
	assert len(mailoutbox) == 1
