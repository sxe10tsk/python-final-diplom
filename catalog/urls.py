from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import CategoryViewSet, ShopViewSet, ProductViewSet, ShopUpdateView

router = DefaultRouter()
router.register('categories', CategoryViewSet, basename='category')
router.register('shops', ShopViewSet, basename='shop')
router.register('products', ProductViewSet, basename='product')

urlpatterns = [
    path('shop/update', ShopUpdateView.as_view(), name='shop-update'),
] + router.urls
