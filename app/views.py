"""
Views for the product catalog.
"""

# Django imports.
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from paypal.standard.forms import PayPalPaymentsForm
from django.core.mail import send_mail

# Project imports.
from app.models import Category, Product, Customer, Order, OrderDetail
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
    context = {'destination_page': request.GET.get('next', '')}
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        destination_page = request.POST['destination_page']

        if authenticated_user := authenticate(request, username=username, password=password):
            login(request, authenticated_user)
            return redirect('app:account' if not destination_page else destination_page)
        else:
            context['message'] = 'Authentication error'
    else:
        if request.user.is_authenticated:
            return redirect('app:account')
    
    return render(request, 'login.html', context)


def logout_user(request: HttpRequest) -> HttpResponse:
    """
    View function to logout a user.
    """
    logout(request)
    return redirect('app:login_user')


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


@login_required(login_url='/users/login/')
def register_order(request: HttpRequest) -> HttpResponse:
    """
    View function to handle order registration.
    """
    user = request.user
    user_data = {'first_name': user.first_name,
                 'last_name': user.last_name,
                 'email': user.email}
    
    if customer := Customer.objects.filter(user=user).first():
        user_data['phone'] = customer.phone
        user_data['address'] = customer.address
    
    return render(request, 'order.html', {'customer_form': CustomerForm(user_data)})


login_required(login_url='/users/login/')
def confirm_order(request: HttpRequest) -> HttpResponse:
    """
    View function to handle order confirmation.
    """
    if request.method == 'POST':
        order_customer = Customer.objects.get(user=request.user)
        total_amount = float(request.session.get('cart_total_amount'))
        new_order = Order()
        new_order.customer = order_customer
        new_order.total_amount = total_amount
        new_order.save()

        order_cart = request.session.get('cart')
        for product_id, product in order_cart.items():
            detail = OrderDetail()
            detail.order = new_order
            detail.product = Product.objects.get(pk=product_id)
            detail.quantity = product['quantity']
            detail.subtotal = product['subtotal']
            detail.save()

        new_order.order_number = 'PED-' + new_order.created_at.strftime('%Y%m%d') + '-' + str(new_order.id)
        new_order.save()

        request.session['order_id'] = new_order.id

        paypal_dict = {
            "business": "sb-fhdlw34638368@business.example.com",
            "amount": total_amount,
            "item_name": 'Order - ' + new_order.order_number,
            "invoice": new_order.order_number,
            "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
            "return": request.build_absolute_uri('/order/thanks'),
            "cancel_return": request.build_absolute_uri('/'),
        }

        cart = Cart(request)
        cart.clear()

        paypal_form = PayPalPaymentsForm(initial=paypal_dict)

    return render(request, 'purchase.html', {'order': new_order, 'paypal_form': paypal_form})


login_required(login_url='/users/login/')
def thanks(request: HttpRequest) -> HttpResponse:
    """
    View function to handle the order confirmation.
    """
    if request.GET.get('PayerID'):
        order = Order.objects.get(pk=request.session.get('order_id'))
        order.status = 'Delivered'
        order.save()
        # send_mail('Order Confirmation',
        #           f'Your order {order.order_number} has been confirmed.',
        #           'emitter@mail.com', [request.user.email])
        return render(request, 'thanks.html', {'order': order})
    return redirect('app:index')

