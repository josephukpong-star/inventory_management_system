import json
from app.models import Product
from app.storage import (save_products, load_products, save_inventory_data, load_inventory_data, save_inventory_report,)
def test_save_products(tmp_path):
    products = [Product(1, "Laptop", 850000, 5), Product(2, "Mouse", 15000, 10),]
    file_path = tmp_path / "products.json"
    save_products(products, file_path)
    with open(file_path, "r") as file:
        data = json.load(file)
    assert data == [{"product_id": 1, "name": "Laptop", "price": 850000, "quantity": 5, "category": "Uncategorized",},{"product_id": 2, "name": "Mouse", "price": 15000, "quantity": 10, "category": "Uncategorized",},]
def test_load_products(tmp_path):
    products = [Product(1, "Laptop", 850000, 5), Product(2, "Mouse", 15000, 10),]
    file_path = tmp_path / "products.json"
    save_products(products, file_path)
    loaded_products = load_products(file_path)
    assert len(loaded_products) == 2
    assert loaded_products[0].product_id == 1
    assert loaded_products[0].name == "Laptop"
    assert loaded_products[0].price == 850000
    assert loaded_products[0].quantity == 5
    assert loaded_products[1].product_id == 2
    assert loaded_products[1].name == "Mouse"
    assert loaded_products[1].price == 15000
    assert loaded_products[1].quantity == 10
def test_load_products_file_not_found(tmp_path):
    file_path = tmp_path / "products.json"
    products = load_products(file_path)
    assert products == []
def test_load_products_invalid_json(tmp_path):
    file_path = tmp_path / "products.json"
    with open(file_path, "w") as file:
        file.write("invalid json")
    products = load_products(file_path)
    assert products == []
def test_category_survives_save_and_load(tmp_path):
    products = [Product(1, "Laptop", 850000, 5, "Electronics")]
    file_path = tmp_path / "products.json"
    save_products(products, file_path)
    loaded_products = load_products(file_path)
    assert loaded_products[0].category == "Electronics"
def test_save_and_load_inventory_data(tmp_path):
    file_path = tmp_path / "inventory.json"
    products = [Product(1, "Laptop", 850000, 10, "Electronics")]
    transactions = [{"product_id": 1, "product_name": "Laptop", "type": "STOCK-IN", "quantity": 5, "price": 850000, "total_value": 4250000, "timestamp": "2026-09-08T21:30:00"}]
    save_inventory_data(products, transactions, file_path)
    loaded_products, loaded_transactions = load_inventory_data(file_path)
    assert loaded_products[0].product_id == 1
    assert loaded_products[0].name == "Laptop"
    assert loaded_products[0].category == "Electronics"
    assert loaded_transactions[0]["product_id"] == 1
    assert loaded_transactions[0]["type"] == "STOCK-IN"
    assert loaded_transactions[0]["quantity"] == 5
    assert loaded_transactions[0]["total_value"] == 4250000
def test_save_inventory_report(tmp_path):
    report = """INVENTORY REPORT
Total Products: 2
Total Quantity: 15
Total Inventory Value: ₦1,000,000.00
"""
    file_path = tmp_path / "inventory_report.txt"
    save_inventory_report(report, file_path)
    with open(file_path, "r", encoding="utf-8") as file:
        saved_report = file.read()
    assert saved_report == report
def test_save_empty_inventory_report(tmp_path):
    report = ""
    file_path = tmp_path / "inventory_report.txt"
    save_inventory_report(report, file_path)
    with open(file_path, "r", encoding="utf-8") as file:
        saved_report = file.read()
    assert saved_report == ""