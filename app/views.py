"""
Views for the product catalog.
"""

# Django imports.
from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse

# Project imports.
from app.models import Category, Product
from app.cart import Cart


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


def get_cart(request: HttpRequest) -> HttpResponse:
    """
    View function for the cart page
    """
    return render(request, 'cart.html')


def add_to_cart(request: HttpRequest, product_id: int) -> HttpResponse:
    """
    View function to add a product to the cart.
    """
    quantity = int(request.POST.get('quantity', 1))
    product = Product.objects.get(pk=product_id)
    cart = Cart(request)
    cart.add(product, quantity)
    return redirect(request.META.get('HTTP_REFERER', '/'))


def remove_from_cart(request: HttpRequest, product_id: int) -> HttpResponse:
    """
    View function to remove a product from the cart.
    """
    cart = Cart(request)
    cart.remove(product_id)
    return redirect(request.META.get('HTTP_REFERER', '/'))


def clear_cart(request: HttpRequest) -> HttpResponse:
    """
    View function to clear the cart.
    """
    cart = Cart(request)
    cart.clear()
    return redirect(request.META.get('HTTP_REFERER', '/'))
    