# modelCart.py
from flask import session
from .entities.cart import Cart, CartItem

class ModelCart:
    @staticmethod
    def add_to_cart(product):
        cart_data = session.get('cart', None)
        if cart_data:
            cart = Cart.from_dict(cart_data)
        else:
            cart = Cart()

        # Check if the product already exists in the cart
        existing_item = next((item for item in cart.items if item.product_id == product.id), None)

        if existing_item:
            # Update quantity and total price
            existing_item.quantity += 1
            existing_item.price += product.price
        else:
            # Add new item
            item = CartItem(product.id, product.name, product.price, 1, product.image)
            cart.add_item(item)

        session['cart'] = cart.to_dict()
        
    @staticmethod
    def remove_from_cart(product_id):
        cart_data = session.get('cart', None)
        if cart_data:
            cart = Cart.from_dict(cart_data)
            cart.remove_item(product_id)
            session['cart'] = cart.to_dict()

    @staticmethod
    def clear_cart():
        session['cart'] = Cart().to_dict()

    @staticmethod
    def get_cart():
        cart_data = session.get('cart', None)
        if cart_data:
            return Cart.from_dict(cart_data)
        else:
            return Cart()
