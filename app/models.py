class Product:
    def __init__(self, product_id, name, price, quantity, category="Uncategorized"):
        if isinstance(product_id, bool) or not isinstance(product_id, int):
            raise ValueError("Product ID must be an integer")
        if product_id <= 0:
            raise ValueError("Product ID must be greater than zero")
        if not name or not name.strip():
            raise ValueError("Product name cannot be empty")
        if isinstance(price, bool) or not isinstance(price, (int, float)):
            raise ValueError("Price must be a number")
        if price < 0:
            raise ValueError("Price cannot be negative")
        if isinstance(quantity, bool) or not isinstance(quantity, int):
            raise ValueError("Quantity must be an integer")
        if quantity < 0:
            raise ValueError("Quantity cannot be negative")
        if not category or not category.strip():
            raise ValueError("Category cannot be empty")
        self.product_id = product_id
        self.name = name.strip().title()
        self.price = price
        self.quantity = quantity
        self.category = category.strip().title()
    def to_dict(self):
        return {"product_id": self.product_id, "name": self.name, "price": self.price, "quantity": self.quantity, "category": self.category,}