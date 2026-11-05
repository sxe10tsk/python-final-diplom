from rest_framework.routers import DefaultRouter
from django.urls import path

from .views import OrderViewSet, ShopOrderViewSet, ShopStateView

router = DefaultRouter()
router.register('order', OrderViewSet, basename='order')
router.register('shop/orders', ShopOrderViewSet, basename='shop-orders')

urlpatterns = [
    path('shop/state', ShopStateView.as_view(), name='shop-state'),] + router.urls