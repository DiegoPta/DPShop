"""
Views for the product catalog.
"""

# Django imports.
from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

# Project imports.
from app.models import Category, Product, Customer
from app.cart import Cart
from app.forms import CustomerForm


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


def login_user(request: HttpRequest) -> HttpResponse:
    """
    View function to login a user.
    """
    context = {}
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if authenticated_user := authenticate(request, username=username, password=password):
            login(request, authenticated_user)
            return redirect('app:account')
        else:
            context['message'] = 'Authentication error'
    
    return render(request, 'login.html', context)


def create_user(request: HttpRequest) -> HttpResponse:
    """
    View function to handle user creation.
    """
    if request.method == 'POST':
        new_username = request.POST.get('new_username')
        new_password = request.POST.get('new_password')
        if new_username and new_password and not User.objects.filter(username=new_username):
            if new_user := User.objects.create_user(username=new_username, password=new_password):
                login(request, new_user)
                return redirect('app:account')
    
    return render(request, 'login.html')


@login_required(login_url='/users/login/')
def get_account(request: HttpRequest) -> HttpResponse:
    """
    View function to handle user account.
    """
    user = request.user
    user_data = {'first_name': user.first_name,
                 'last_name': user.last_name,
                 'email': user.email}
    
    if request.method == 'POST':
        customer_form = CustomerForm(request.POST)
        if customer_form.is_valid():
            customer_data = customer_form.cleaned_data
            
            # Update user data
            for field in ['first_name', 'last_name', 'email']:
                if field in customer_data:
                    setattr(user, field, customer_data[field])
                    customer_data.pop(field)
            user.save()

            Customer.objects.update_or_create(defaults=customer_data, user=user)

    elif customer := Customer.objects.filter(user=user).first():
        user_data['document_id'] = customer.document_id
        user_data['gender'] = customer.gender
        user_data['birthdate'] = customer.birthdate
        user_data['phone'] = customer.phone
        user_data['address'] = customer.address
        
    return render(request, 'account.html', {'customer_form': CustomerForm(user_data)})
