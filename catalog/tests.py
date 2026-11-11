import pytest
from rest_framework import status

@pytest.mark.django_db
def test_products_list_public(client, product_info):
	response = client.get('/api/v1/products/')
	assert response.status_code == status.HTTP_200_OK
	assert response.data['count'] == 1

@pytest.mark.django_db
def test_product_detail(client, product, product_info):
	response = client.get(f'/api/v1/products/{product.pk}/')
	assert response.status_code == status.HTTP_200_OK
	assert len(response.data['product_infos']) == 1
	assert response.data['product_infos'][0]['price'] == '200.00'

@pytest.mark.django_db
def test_filter_by_category(client, category, product_info):
	response = client.get(f'/api/v1/products/?category={category.pk}')
	assert response.data['count'] == 1

@pytest.mark.django_db
def test_search(client, product_info):
	response = client.get('/api/v1/products/?search=Test')
	assert response.data['count'] == 1

@pytest.mark.django_db
def test_shops_list(client, shop):
	response = client.get('/api/v1/shops/')
	assert response.status_code == status.HTTP_200_OK
	assert response.data['count'] == 1
