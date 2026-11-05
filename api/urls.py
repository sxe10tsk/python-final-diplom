from django.urls import include, path
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

urlpatterns = [
	path('', include('users.urls')),
	path('', include('catalog.urls')),
	path('', include('cart.urls')),
	path('', include('orders_api.urls')),
	path('', include(router.urls)),
]

