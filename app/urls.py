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
]