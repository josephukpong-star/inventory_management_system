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

def test_create_product_with_configurable_units():
    product = Product(101, "Eggs", 150, 300, "Food", base_unit="piece", purchase_units=[{"name": "crate", "base_quantity": 30},], selling_units=[{"name": "crate", "base_quantity": 30}, {"name": "half crate", "base_quantity": 15}, {"name": "piece", "base_quantity": 1},],)

    assert product.base_unit == "piece"
    assert product.quantity == 300
    assert product.purchase_units == [{"name": "crate", "base_quantity": 30},]
    assert product.selling_units == [{"name": "crate", "base_quantity": 30}, {"name": "half crate", "base_quantity": 15}, {"name": "piece", "base_quantity": 1},]

def test_product_to_dict_includes_configurable_units():
    product = Product(101, "Eggs", 150, 300, base_unit="piece", purchase_units=[{"name": "crate", "base_quantity": 30},], selling_units=[{"name": "half crate", "base_quantity": 15}, {"name": "piece", "base_quantity": 1},],)

    result = product.to_dict()

    assert result["base_unit"] == "piece"
    assert result["purchase_units"] == [{"name": "crate", "base_quantity": 30},]
    assert result["selling_units"] == [{"name": "half crate", "base_quantity": 15},{"name": "piece", "base_quantity": 1},]

def test_product_rejects_zero_purchase_conversion_factor():
    with pytest.raises(ValueError, match="greater than zero"):
        Product(101, "Eggs", 150, 300, base_unit="piece", purchase_units=[{"name": "crate", "base_quantity": 0},],)

def test_product_rejects_negative_selling_conversion_factor():
    with pytest.raises(ValueError, match="greater than zero"):
        Product(101, "Eggs", 150, 300, base_unit="piece", selling_units=[{"name": "half crate", "base_quantity": -15},],)

def test_product_rejects_duplicate_purchase_unit_names():
    with pytest.raises(ValueError, match="Duplicate purchase unit name"):
        Product(101, "Eggs", 150, 300, base_unit="piece", purchase_units=[{"name": "crate", "base_quantity": 30}, {"name": "CRATE", "base_quantity": 30},],)