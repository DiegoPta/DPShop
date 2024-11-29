"""
Url router for the main application.
"""

# Django imports.
from django.urls import path

# Project imports.
from app import views


app_name = 'app'

urlpatterns = [
    path('', views.index, name='index'),
    path('products/category/<int:category_id>', views.products_by_category, name='products_by_category'),
    # path('products/filter', views.products_by_name, name='products_by_name'),
    path('products/<int:product_id>', views.get_product_by_id, name='product_details'),
    path('cart/', views.get_cart, name='cart'),
    path('cart/add/<int:product_id>', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>', views.remove_from_cart, name='remove_from_cart'),
    path('cart/clear/', views.clear_cart, name='clear_cart'),
]