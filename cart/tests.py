from urllib import response

import pytest
from rest_framework import status

@pytest.mark.django_db
def test_add_to_cart(auth_client, product_info):
	response = auth_client.post('/api/v1/cart/', {
		'product_info_id': product_info.id,
		'quantity': 2
	}, format='json')
	assert response.status_code == status.HTTP_201_CREATED
	assert response.data['total_items'] == 2

@pytest.mark.django_db
def add_same_increases_quantity(auth_client, product_info):
	auth_client.post('/api/v1/cart/', {
		'product_info.id': product_info.id,
		'quantity':2
	}, format='json')
	response = auth_client.post('/api/v1/cart/', {
		'product_info_id': product_info.id,
		'quantity':3
	}, format='json')
	assert response.status_code == status.HTTP_200_OK
	assert response.data['total_items'] == 5

@pytest.mark.django_db
def test_out_of_stock(auth_client, product_info):
	 response = auth_client.post('/api/v1/cart/', {
		 'product_info_id': product_info.id,
		 'quantity': 9999
	}, format='json')
	 assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.django_db
def test_shop_is_closed(auth_client, product_info, shop):
	shop.is_open = False
	shop.save()
	response = auth_client.post('/api/v1/cart/', {
		'product_info_id': product_info.id,
		'quantity': 2,
	}, format='json')
	assert response.status_code == status.HTTP_400_BAD_REQUEST