import pytest
from django.contrib.auth import get_user_model
from rest_framework import status

User = get_user_model()

@pytest.mark.django_db
def test_register_send_email(api_client, mailoutbox):
	response = api_client.post('/api/v1/user/register', {
	                       'email': 'test@email.com',
	                       'password': 'userpassword12345',
	                       'password_confirmation': 'userpassword12345',
	                       'user_type': 'customer',
	}, format='json')
	assert response.status_code == status.HTTP_201_CREATED
	assert len(mailoutbox) == 1
	assert 'test@email.com' in mailoutbox[0].to
	user = User.objects.get(email='test@email.com')
	assert user.is_active is False
	assert user.check_password('userpassword12345')


@pytest.mark.django_db
def test_login_after_activation(api_client):
	user = User.objects.create_user(email='test@email.com', password='userpassword12345')
	user.is_active = True
	user.save()
	response = api_client.post(
		'/api/v1/user/login', {
			'email': 'test@email.com',
			'password': 'userpassword12345',
		}, format='json'
		)
	assert response.status_code == status.HTTP_200_OK
	assert 'token' in response.data

@pytest.mark.django_db
def test_login_inactive_user(client):
	User.objects.create_user(email='test@email.com', password='userpassword12345')
	response = client.post(
		'/api/v1/user/login', {
			'email': 'test@email.com',
			'password': 'userpassword12345',
		}, format='json'
		)
	assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.django_db
def test_create_contact(auth_client):
	response = auth_client.post(
		'/api/v1/user/contact', {
			'city': 'test city',
			'street': 'test street',
			'house': '111',
			'phone': '+7987654321',
		}, format='json'
	)
	assert response.status_code == status.HTTP_201_CREATED
	assert response.data['city'] == 'test city'

@pytest.mark.django_db
def test_only_own_contacts(auth_client, user):
	from users.models import Contact
	other_user = User.objects.create_user(email='other@mail.com', password='anotherpass12345')
	Contact.objects.create(
		user=other_user,
		city='another city',
		street='another street',
		house='999',
		phone='999',
	)
	response = auth_client.get('/api/v1/user/contact')
	assert response.status_code == status.HTTP_200_OK
	assert response.data['count'] == 0

def test_contact_requires_auth(client):
	response = client.get('/api/v1/user/contact')
	assert response.status_code == status.HTTP_401_UNAUTHORIZED
