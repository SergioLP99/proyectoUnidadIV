class CartItem:
    def __init__(self, product_id, name, price, quantity, image):
        self.product_id = product_id
        self.name = name
        self.price = price
        self.quantity = quantity
        self.image = image

    def to_dict(self):
        return {
            'product_id': self.product_id,
            'name': self.name,
            'price': self.price,
            'quantity': self.quantity,
            'image': self.image
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            product_id=data['product_id'],
            name=data['name'],
            price=data['price'],
            quantity=data['quantity'],
            image=data['image']
        )

    def __repr__(self):
        return f"CartItem(product_id={self.product_id}, name={self.name}, price={self.price}, quantity={self.quantity}, image={self.image})"

class Cart:
    def __init__(self):
        self.items = []

    def add_item(self, item):
        self.items.append(item)

    def remove_item(self, product_id):
        self.items = [item for item in self.items if item.product_id != product_id]

    def clear(self):
        self.items = []

    def get_total_price(self):
        return sum(item.price * item.quantity for item in self.items)

    def to_dict(self):
        return {
            'items': [item.to_dict() for item in self.items]
        }

    @classmethod
    def from_dict(cls, data):
        cart = cls()
        cart.items = [CartItem.from_dict(item) for item in data['items']]
        return cart

    def __repr__(self):
        return f"Cart(items={self.items})"
