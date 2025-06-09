from django.urls import path
from .views import (
    CategoryAPIView,
    ProductsAPIView,
    OrderAPIView,
)

urlpatterns = [
    path('categories/', CategoryAPIView.as_view(), name='category-list'),
    path('products/', ProductsAPIView.as_view(), name='product-list'),
    path('products/<int:category_id>/', ProductsAPIView.as_view(), name='products-by-category'),
    path('order/', OrderAPIView.as_view(), name='order-create'),
]
