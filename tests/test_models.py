import pytest
from app.models import Product
def test_create_product():
    product = Product(1, "Laptop", 850000, 5)
    assert product.product_id == 1
    assert product.name == "Laptop"
    assert product.price == 850000
    assert product.quantity == 5
def test_product_to_dict():
    product = Product(1, "Laptop", 850000, 5)
    result = product.to_dict()
    assert result == {"product_id": 1, "name": "Laptop", "price": 850000, "quantity": 5, "category": "Uncategorized"}
def test_negative_price_raises_error():
    with pytest.raises(ValueError, match="Price cannot be negative"):
        Product(1, "Laptop", -5000, 5)
def test_negative_quantity_raises_error():
    with pytest.raises(ValueError, match="Quantity cannot be negative"):
        Product(1, "Laptop", 850000, -2)
def test_create_product_with_category():
    product = Product(1, "Laptop", 850000, 10, "Electronics")
    assert product.category == "Electronics"
def test_product_to_dict_includes_category():
    product = Product(1, "Laptop", 850000, 10, "Electronics")
    result = product.to_dict()
    assert result["category"] == "Electronics"