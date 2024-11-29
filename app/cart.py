"""
Definition of the Cart class representing the shopping cart.
"""

# Django imports.
from django.http import HttpRequest

# Project imports.
from app.models import Product


class Cart:

    def __init__(self, request: HttpRequest) -> None:
        """
        Initializes the Cart object.
        """
        self.request = request
        self.session = request.session
        cart = self.session.get('cart')
        total_amount = self.session.get('cart_total_amount')

        if not cart:
            cart = self.session['cart'] = {}
            total_amount = self.session['cart_total_amount'] = '0'

        self.cart = cart
        self.total_amount = float(total_amount)
        

    def add(self, product: Product, quantity: int) -> None:
        """
        Adds a product to the cart.
        """
        product_id = str(product.id)
        if not product_id in self.cart:
            self.cart[product_id] = {
                'product_id': product.id,
                'name': product.name,
                'price': str(product.price),
                'image': product.image.url,
                'quantity': quantity,
                'category': str(product.category),
                'subtotal': str(product.price * quantity)
            }
        else:
            self.cart[product_id]['quantity'] += quantity
            self.cart[product_id]['subtotal'] = str(product.price * self.cart[product_id]['quantity'])

        self.save()
        
    def remove(self, product_id: int) -> None:
        """
        Removes a product from the cart.
        """
        if self.cart.pop(str(product_id)):
            self.save()

    def clear(self) -> None:
        """
        Clears the cart.
        """
        self.session['cart'] = {}
        self.session['cart_total_amount'] = '0'

    def save(self) -> None:
        """
        Saves the cart.
        """
        self.session['cart_total_amount'] = str(sum([float(product['subtotal']) for product in self.cart.values()]))
        self.session['cart'] = self.cart
        self.session.modified = True
