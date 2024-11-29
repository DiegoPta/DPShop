"""
Views for the product catalog.
"""

# Django imports.
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse

# Project imports.
from app.models import Category, Product


def index(request: HttpRequest) -> HttpResponse:
    """
    View function for the product catalog index page
    """
    if name := request.GET.get('name'):
        products = Product.objects.filter(name__icontains=name)
    else:
        products = Product.objects.all()
    categories = Category.objects.all()
    return render(request, 'index.html', {'products': products, 'categories': categories})


def products_by_category(request: HttpRequest, category_id: int) -> HttpResponse:
    """
    View function for the product catalog by category id.
    """
    category = Category.objects.get(pk=category_id)
    products = category.products.all()
    categories = Category.objects.all()
    return render(request, 'index.html', {'products': products, 'categories': categories})


# def products_by_name(request: HttpRequest) -> HttpResponse:
#     """
#     View function for the product catalog by product name
#     """
#     if name := request.GET.get('name'):
#         products = Product.objects.filter(name__icontains=name)
#         categories = Category.objects.all()
#         return render(request, 'index.html', {'products': products, 'categories': categories})
#     return index()


def get_product_by_id(request: HttpRequest, product_id: int) -> HttpResponse:
    """
    View function for the product catalog by product id.
    """
    product = Product.objects.get(pk=product_id)
    return render(request, 'product.html', {'product': product})
