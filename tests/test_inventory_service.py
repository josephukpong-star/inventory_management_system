import pytest
from app.models import Product
from app.inventory_service import InventoryService
from app.storage import save_products, load_products
def test_add_product():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 5)
    inventory.add_product(product)
    assert len(inventory.products) == 1
    assert inventory.products[0].name == "Laptop"
def test_get_all_products():
    inventory = InventoryService()
    product1 = Product(1, "Laptop", 850000, 5)
    product2 = Product(2, "Mouse", 15000, 10)
    inventory.add_product(product1)
    inventory.add_product(product2)
    products = inventory.get_all_products()
    assert len(products) == 2
    assert products[0].name == "Laptop"
    assert products[1].name == "Mouse"
def test_add_duplicate_product_raises_error():
    inventory = InventoryService()
    product1 = Product(1, "Laptop", 850000, 5)
    product2 = Product(1, "Mouse", 15000, 10)
    inventory.add_product(product1)
    with pytest.raises(ValueError, match="Product ID already exists"):
        inventory.add_product(product2)
def test_get_product():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 5)
    inventory.add_product(product)
    result = inventory.get_product(1)
    assert result == product
def test_get_product_not_found():
    inventory = InventoryService()
    with pytest.raises(ValueError, match="Product not found"):
        inventory.get_product(999)
def test_update_product_quantity():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 5)
    inventory.add_product(product)
    inventory.update_quantity(1, 3)
    assert product.quantity == 8
def test_update_product_quantity_not_found():
    inventory = InventoryService()
    with pytest.raises(ValueError, match="Product not found"):
        inventory.update_quantity(999, 3)
def test_update_quantity_cannot_go_negative():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 5)
    inventory.add_product(product)
    with pytest.raises(ValueError, match="Quantity cannot be negative"):
        inventory.update_quantity(1, -10)
def test_remove_product():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 5)
    inventory.add_product(product)
    inventory.remove_product(1)
    assert len(inventory.products) == 0
def test_remove_product_not_found():
    inventory = InventoryService()
    with pytest.raises(ValueError, match="Product not found"):
        inventory.remove_product(999)
def test_calculate_total_value_with_products():
    inventory = InventoryService()
    product1 = Product(1, "Laptop", 850000, 5)
    product2 = Product(2, "Mouse", 15000, 10)
    inventory.add_product(product1)
    inventory.add_product(product2)
    total = inventory.calculate_total_value()
    assert total == 4400000
def test_calculate_total_value_empty_inventory():
    inventory = InventoryService()
    total = inventory.calculate_total_value()
    assert total == 0
def test_get_low_stock_products():
    inventory = InventoryService()
    product1 = Product(1, "Laptop", 850000, 2)
    product2 = Product(2, "Mouse", 15000, 10)
    product3 = Product(3, "Keyboard", 30000, 5)
    inventory.add_product(product1)
    inventory.add_product(product2)
    inventory.add_product(product3)
    low_stock_products = inventory.get_low_stock_products(5)
    assert len(low_stock_products) == 2
    assert product1 in low_stock_products
    assert product3 in low_stock_products
def test_get_low_stock_products_rejects_negative_threshold():
    inventory = InventoryService()
    with pytest.raises(ValueError, match="Low stock threshold cannot be negative"):
        inventory.get_low_stock_products(-1)
def test_get_low_stock_products_rejects_non_integer_threshold():
    inventory = InventoryService()
    with pytest.raises(ValueError, match="Low stock threshold must be an integer"):
        inventory.get_low_stock_products("5")
def test_get_low_stock_products_rejects_boolean_threshold():
    inventory = InventoryService()
    with pytest.raises(ValueError, match="Low stock threshold must be an integer"):
        inventory.get_low_stock_products(True)
def test_get_low_stock_products_empty():
    inventory = InventoryService()
    low_stock_products = inventory.get_low_stock_products(5)
    assert low_stock_products == []
def test_search_products_by_name():
    inventory = InventoryService()
    product1 = Product(1, "Laptop", 850000, 5)
    product2 = Product(2, "Gaming Laptop", 1200000, 3)
    product3 = Product(3, "Mouse", 15000, 10)
    inventory.add_product(product1)
    inventory.add_product(product2)
    inventory.add_product(product3)
    results = inventory.search_products("laptop")
    assert len(results) == 2
    assert product1 in results
    assert product2 in results
def test_search_products_case_insensitive():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 5)
    inventory.add_product(product)
    results = inventory.search_products("LAPTOP")
    assert product in results
def test_search_products_not_found():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 5)
    inventory.add_product(product)
    results = inventory.search_products("Phone")
    assert results == []
def test_get_inventory_summary():
    inventory = InventoryService()
    product1 = Product(1, "Laptop", 850000, 5)
    product2 = Product(2, "Mouse", 15000, 10)
    product3 = Product(3, "Keyboard", 30000, 2)
    inventory.add_product(product1)
    inventory.add_product(product2)
    inventory.add_product(product3)
    summary = inventory.get_inventory_summary()
    assert summary["total_products"] == 3
    assert summary["total_quantity"] == 17
    assert summary["total_value"] == 4460000
    assert summary["low_stock_count"] == 2
def test_save_and_load_inventory(tmp_path):
    file_path = tmp_path / "products.json"
    inventory = InventoryService()
    product1 = Product(1, "Laptop", 850000, 5)
    product2 = Product(2, "Mouse", 15000, 10)
    inventory.add_product(product1)
    inventory.add_product(product2)
    save_products(inventory.get_all_products(), file_path)
    loaded_products = load_products(file_path)
    assert len(loaded_products) == 2
    assert loaded_products[0].name == "Laptop"
    assert loaded_products[1].name == "Mouse"
def test_removed_products_survive_save_and_load(tmp_path):
    file_path = tmp_path / "inventory.json"
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 5, "Electronics")
    inventory.add_product(product)
    inventory.remove_product(1)
    inventory.save_inventory(file_path)
    loaded_inventory = InventoryService()
    loaded_inventory.load_inventory(file_path)
    assert loaded_inventory.products == []
    assert len(loaded_inventory.removed_products) == 1
    assert loaded_inventory.removed_products[0].product_id == 1
    assert loaded_inventory.removed_products[0].name == "Laptop"
    assert loaded_inventory.removed_products[0].category == "Electronics"
def test_deleted_products_history_survives_save_and_load(tmp_path):
    file_path = tmp_path / "inventory.json"
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 5, "Electronics")
    inventory.add_product(product)
    inventory.remove_product(1)
    inventory.permanently_delete_product(1)
    inventory.save_inventory(file_path)
    loaded_inventory = InventoryService()
    loaded_inventory.load_inventory(file_path)
    assert loaded_inventory.products == []
    assert loaded_inventory.removed_products == []
    assert len(loaded_inventory.deleted_products) == 1
    deleted_record = loaded_inventory.deleted_products[0]
    assert deleted_record["record_id"] == 1
    assert deleted_record["product"]["product_id"] == 1
    assert deleted_record["product"]["name"] == "Laptop"
    assert deleted_record["product"]["category"] == "Electronics"
    assert deleted_record["action"] == "PERMANENT_DELETE"
def test_deleted_record_counter_survives_save_and_load(tmp_path):
    file_path = tmp_path / "inventory.json"
    inventory = InventoryService()
    product1 = Product(1, "Laptop", 850000, 5, "Electronics")
    product2 = Product(2, "Mouse", 15000, 10, "Accessories")
    product3 = Product(3, "Keyboard", 25000, 8, "Accessories")
    inventory.add_product(product1)
    inventory.add_product(product2)
    inventory.add_product(product3)
    inventory.remove_product(1)
    inventory.permanently_delete_product(1)
    inventory.remove_product(2)
    inventory.permanently_delete_product(2)
    inventory.save_inventory(file_path)
    loaded_inventory = InventoryService()
    loaded_inventory.load_inventory(file_path)
    assert loaded_inventory.deleted_record_counter == 2
    loaded_inventory.remove_product(3)
    loaded_inventory.permanently_delete_product(3)
    assert loaded_inventory.deleted_record_counter == 3
    assert loaded_inventory.deleted_products[-1]["record_id"] == 3
def test_inventory_save_inventory(tmp_path):
    file_path = tmp_path / "products.json"
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 5)
    inventory.add_product(product)
    inventory.save_inventory(file_path)
    loaded_products = load_products(file_path)
    assert len(loaded_products) == 1
    assert loaded_products[0].name == "Laptop"
    assert loaded_products[0].quantity == 5
def test_inventory_load_inventory(tmp_path):
    file_path = tmp_path / "products.json"
    products = [Product(1, "Laptop", 850000, 5), Product(2, "Mouse", 15000, 10),]
    save_products(products, file_path)
    inventory = InventoryService()
    inventory.load_inventory(file_path)
    assert len(inventory.products) == 2
    assert inventory.products[0].name == "Laptop"
    assert inventory.products[1].name == "Mouse"
def test_calculate_total_inventory_value_from_dicts():
    products = [{"name": "Laptop", "price": 500000, "quantity": 2}, {"name": "Mouse", "price": 15000, "quantity": 5}, {"name": "Keyboard", "price": 25000, "quantity": 3},]
    service = InventoryService()
    total_value = service.calculate_total_inventory_value(products)
    assert total_value == 1150000
def test_get_out_of_stock_products():
    service = InventoryService()
    service.add_product(Product(1, "Laptop", 500000, 5))
    service.add_product(Product(2, "Mouse", 15000, 0))
    service.add_product(Product(3, "Keyboard", 25000, 0))
    out_of_stock = service.get_out_of_stock_products()
    assert len(out_of_stock) == 2
    assert out_of_stock[0].name == "Mouse"
    assert out_of_stock[1].name == "Keyboard"
def test_get_out_of_stock_products_empty():
    service = InventoryService()
    service.add_product(Product(1, "Laptop", 500000, 5))
    service.add_product(Product(2, "Mouse", 15000, 10))
    out_of_stock = service.get_out_of_stock_products()
    assert out_of_stock == []
def test_inventory_summary_includes_out_of_stock_count():
    service = InventoryService()
    service.add_product(Product(1, "Laptop", 500000, 10))
    service.add_product(Product(2, "Mouse", 15000, 0))
    service.add_product(Product(3, "Keyboard", 25000, 0))
    service.add_product(Product(4, "Monitor", 200000, 8))
    summary = service.get_inventory_summary()
    assert summary["out_of_stock_count"] == 2
def test_inventory_summary_uses_custom_low_stock_threshold():
    service = InventoryService()
    service.add_product(Product(1, "Laptop", 500000, 8))
    service.add_product(Product(2, "Mouse", 15000, 6))
    service.add_product(Product(3, "Keyboard", 25000, 3))
    summary = service.get_inventory_summary(low_stock_threshold=7)
    assert summary["low_stock_count"] == 2
def test_inventory_summary_rejects_negative_low_stock_threshold():
    service = InventoryService()
    with pytest.raises(ValueError, match="Low stock threshold cannot be negative"):
        service.get_inventory_summary(low_stock_threshold=-1)
def test_inventory_summary_rejects_non_integer_low_stock_threshold():
    service = InventoryService()
    with pytest.raises(ValueError, match="Low stock threshold must be an integer"):
        service.get_inventory_summary(low_stock_threshold=5.5)
def test_inventory_summary_rejects_boolean_low_stock_threshold():
    service = InventoryService()
    with pytest.raises(ValueError, match="Low stock threshold must be an integer"):
        service.get_inventory_summary(low_stock_threshold=True)
def test_get_product_stock_status():
    service = InventoryService()
    service.add_product(Product(1, "Laptop", 500000, 10))
    service.add_product(Product(2, "Mouse", 15000, 3))
    service.add_product(Product(3, "Keyboard", 25000, 0))
    assert service.get_product_stock_status(1) == "IN STOCK"
    assert service.get_product_stock_status(2) == "LOW STOCK"
    assert service.get_product_stock_status(3) == "OUT OF STOCK"
def test_get_product_stock_status_with_custom_threshold():
    service = InventoryService()
    service.add_product(Product(1, "Laptop", 500000, 8))
    status = service.get_product_stock_status(1, low_stock_threshold=10)
    assert status == "LOW STOCK"
def test_stock_in_increases_product_quantity():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 10)
    inventory.add_product(product)
    inventory.stock_in(1, 5)
    assert product.quantity == 15
def test_stock_in_rejects_zero_quantity():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 10)
    inventory.add_product(product)
    with pytest.raises(ValueError, match="Stock-in quantity must be greater than zero"):
        inventory.stock_in(1, 0)
def test_stock_in_rejects_negative_quantity():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 10)
    inventory.add_product(product)
    with pytest.raises(ValueError, match="Stock-in quantity must be greater than zero"):
        inventory.stock_in(1, -5)
def test_stock_out_decreases_product_quantity():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 10)
    inventory.add_product(product)
    inventory.stock_out(1, 3)
    assert product.quantity == 7
def test_stock_out_cannot_exceed_available_quantity():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 10)
    inventory.add_product(product)
    with pytest.raises(ValueError, match="Quantity cannot be negative"):
        inventory.stock_out(1, 15)
    assert product.quantity == 10
def test_stock_out_all_available_quantity():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 10)
    inventory.add_product(product)
    inventory.stock_out(1, 10)
    assert product.quantity == 0
    assert inventory.get_product_stock_status(1) == "OUT OF STOCK"
def test_stock_out_rejects_zero_quantity():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 10)
    inventory.add_product(product)
    with pytest.raises(ValueError, match="Stock-out quantity must be greater than zero"):
        inventory.stock_out(1, 0)
    assert product.quantity == 10
def test_stock_out_rejects_negative_quantity():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 10)
    inventory.add_product(product)
    with pytest.raises(
        ValueError,
        match="Stock-out quantity must be greater than zero"):
        inventory.stock_out(1, -5)
    assert product.quantity == 10
def test_stock_out_records_transaction():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 10)
    inventory.add_product(product)
    inventory.stock_out(1, 3)
    transactions = inventory.get_transactions()
    assert len(transactions) == 1
    assert transactions[0]["product_id"] == 1
    assert transactions[0]["type"] == "STOCK-OUT"
    assert transactions[0]["quantity"] == 3
def test_transaction_history_preserves_order():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 10)
    inventory.add_product(product)
    inventory.stock_in(1, 5)
    inventory.stock_out(1, 3)
    inventory.stock_in(1, 10)
    transactions = inventory.get_transactions()
    assert len(transactions) == 3
    assert transactions[0]["type"] == "STOCK-IN"
    assert transactions[0]["quantity"] == 5
    assert transactions[1]["type"] == "STOCK-OUT"
    assert transactions[1]["quantity"] == 3
    assert transactions[2]["type"] == "STOCK-IN"
    assert transactions[2]["quantity"] == 10
    assert product.quantity == 22
def test_stock_in_records_transaction_timestamp():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 10)
    inventory.add_product(product)
    inventory.stock_in(1, 5)
    transactions = inventory.get_transactions()
    assert len(transactions) == 1
    assert "timestamp" in transactions[0]
    assert transactions[0]["timestamp"] is not None
def test_stock_out_records_transaction_timestamp():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 10)
    inventory.add_product(product)
    inventory.stock_out(1, 3)
    transactions = inventory.get_transactions()
    assert len(transactions) == 1
    assert "timestamp" in transactions[0]
    assert transactions[0]["timestamp"] is not None
def test_stock_in_transaction_timestamp_is_valid_iso_format():
    from datetime import datetime
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 10)
    inventory.add_product(product)
    inventory.stock_in(1, 5)
    transactions = inventory.get_transactions()
    timestamp = transactions[0]["timestamp"]
    parsed_timestamp = datetime.fromisoformat(timestamp)
    assert parsed_timestamp is not None
def test_stock_out_transaction_timestamp_is_valid_iso_format():
    from datetime import datetime
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 10)
    inventory.add_product(product)
    inventory.stock_out(1, 3)
    transactions = inventory.get_transactions()
    timestamp = transactions[0]["timestamp"]
    parsed_timestamp = datetime.fromisoformat(timestamp)
    assert parsed_timestamp is not None
def test_transaction_timestamps_preserve_order():
    from datetime import datetime
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 10)
    inventory.add_product(product)
    inventory.stock_in(1, 5)
    inventory.stock_out(1, 3)
    transactions = inventory.get_transactions()
    first_timestamp = datetime.fromisoformat(transactions[0]["timestamp"])
    second_timestamp = datetime.fromisoformat(transactions[1]["timestamp"])
    assert first_timestamp <= second_timestamp
def test_stock_in_transaction_records_product_name():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 10)
    inventory.add_product(product)
    inventory.stock_in(1, 5)
    transactions = inventory.get_transactions()
    assert transactions[0]["product_name"] == "Laptop"
def test_stock_out_transaction_records_product_name():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 10)
    inventory.add_product(product)
    inventory.stock_out(1, 3)
    transactions = inventory.get_transactions()
    assert transactions[0]["product_name"] == "Laptop"
def test_stock_in_transaction_records_product_price():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 10)
    inventory.add_product(product)
    inventory.stock_in(1, 5)
    transactions = inventory.get_transactions()
    assert transactions[0]["price"] == 850000
def test_stock_out_transaction_records_product_price():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 10)
    inventory.add_product(product)
    inventory.stock_out(1, 3)
    transactions = inventory.get_transactions()
    assert transactions[0]["price"] == 850000
def test_stock_in_transaction_records_total_value():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 10)
    inventory.add_product(product)
    inventory.stock_in(1, 5)
    transactions = inventory.get_transactions()
    assert transactions[0]["total_value"] == 4250000
def test_stock_out_transaction_records_total_value():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 10)
    inventory.add_product(product)
    inventory.stock_out(1, 3)
    transactions = inventory.get_transactions()
    assert transactions[0]["total_value"] == 2550000
def test_transaction_preserves_price_at_transaction_time():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 10)
    inventory.add_product(product)
    inventory.stock_in(1, 2)
    # Change the product price after the transaction
    product.price = 900000
    transactions = inventory.get_transactions()
    assert transactions[0]["price"] == 850000
    assert transactions[0]["total_value"] == 1700000
def test_stock_out_transaction_preserves_price_at_transaction_time():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 10)
    inventory.add_product(product)
    inventory.stock_out(1, 2)
    # Change the product price after the transaction
    product.price = 900000
    transactions = inventory.get_transactions()
    assert transactions[0]["price"] == 850000
    assert transactions[0]["total_value"] == 1700000
def test_get_transactions_empty_inventory():
    inventory = InventoryService()
    transactions = inventory.get_transactions()
    assert transactions == []
def test_transaction_history_records_all_transactions():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 20)
    inventory.add_product(product)
    inventory.stock_in(1, 5)
    inventory.stock_out(1, 3)
    inventory.stock_in(1, 7)
    inventory.stock_out(1, 2)
    transactions = inventory.get_transactions()
    assert len(transactions) == 4
def test_transaction_contains_all_required_details():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 10)
    inventory.add_product(product)
    inventory.stock_in(1, 5)
    transaction = inventory.get_transactions()[0]
    assert transaction["product_id"] == 1
    assert transaction["product_name"] == "Laptop"
    assert transaction["price"] == 850000
    assert transaction["type"] == "STOCK-IN"
    assert transaction["quantity"] == 5
    assert transaction["total_value"] == 4250000
    assert "timestamp" in transaction
def test_stock_out_transaction_contains_all_required_details():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 10)
    inventory.add_product(product)
    inventory.stock_out(1, 3)
    transaction = inventory.get_transactions()[0]
    assert transaction["product_id"] == 1
    assert transaction["product_name"] == "Laptop"
    assert transaction["price"] == 850000
    assert transaction["type"] == "STOCK-OUT"
    assert transaction["quantity"] == 3
    assert transaction["total_value"] == 2550000
    assert "timestamp" in transaction
def test_get_transactions_returns_copy():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 10)
    inventory.add_product(product)
    inventory.stock_in(1, 5)
    transactions = inventory.get_transactions()
    transactions.clear()
    assert len(inventory.get_transactions()) == 1
def test_get_all_products_returns_copy():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 10)
    inventory.add_product(product)
    products = inventory.get_all_products()
    products.clear()
    assert len(inventory.get_all_products()) == 1
def test_remove_product_removes_product_from_inventory():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 10)
    inventory.add_product(product)
    inventory.remove_product(1)
    assert inventory.get_all_products() == []
def test_remove_nonexistent_product_raises_error():
    inventory = InventoryService()
    with pytest.raises(ValueError, match="Product not found"):
        inventory.remove_product(999)
def test_total_inventory_value_updates_after_stock_changes():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 10)
    inventory.add_product(product)
    assert inventory.calculate_total_value() == 8500000
    inventory.stock_in(1, 5)
    assert inventory.calculate_total_value() == 12750000
    inventory.stock_out(1, 3)
    assert inventory.calculate_total_value() == 10200000
def test_inventory_summary_updates_after_stock_changes():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 10)
    inventory.add_product(product)
    summary = inventory.get_inventory_summary()
    assert summary["total_products"] == 1
    assert summary["total_quantity"] == 10
    assert summary["total_value"] == 8500000
    inventory.stock_in(1, 5)
    summary = inventory.get_inventory_summary()
    assert summary["total_quantity"] == 15
    assert summary["total_value"] == 12750000
    inventory.stock_out(1, 3)
    summary = inventory.get_inventory_summary()
    assert summary["total_quantity"] == 12
    assert summary["total_value"] == 10200000
def test_search_products_by_category():
    inventory = InventoryService()
    laptop = Product(1, "Laptop", 850000, 10, "Electronics")
    printer = Product(2, "Printer", 350000, 5, "Electronics")
    chair = Product(3, "Office Chair", 120000, 8, "Furniture")
    inventory.add_product(laptop)
    inventory.add_product(printer)
    inventory.add_product(chair)
    results = inventory.search_products_by_category("Electronics")
    assert len(results) == 2
    assert results[0].name == "Laptop"
    assert results[1].name == "Printer"
def test_search_products_by_category_returns_empty_when_no_match():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 10, "Electronics")
    inventory.add_product(product)
    results = inventory.search_products_by_category("Furniture")
    assert results == []
def test_search_products_by_category_ignores_extra_spaces():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 10, "Electronics")
    inventory.add_product(product)
    results = inventory.search_products_by_category("  Electronics  ")
    assert len(results) == 1
    assert results[0].name == "Laptop"
def test_get_products_by_category():
    inventory = InventoryService()
    inventory.add_product(Product(1, "Laptop", 850000, 10, "Electronics"))
    inventory.add_product(Product(2, "Printer", 350000, 5, "Electronics"))
    inventory.add_product(Product(3, "Office Chair", 120000, 8, "Furniture"))
    results = inventory.get_products_by_category("Electronics")
    assert len(results) == 2
    assert results[0].category == "Electronics"
    assert results[1].category == "Electronics"
def test_get_products_by_category_returns_empty_when_no_match():
    inventory = InventoryService()
    inventory.add_product(Product(1, "Laptop", 850000, 10, "Electronics"))
    results = inventory.get_products_by_category("Furniture")
    assert results == []
def test_get_products_by_category_ignores_case_and_spaces():
    inventory = InventoryService()
    inventory.add_product(Product(1, "Laptop", 850000, 10, "Electronics"))
    results = inventory.get_products_by_category("  ELECTRONICS  ")
    assert len(results) == 1
    assert results[0].name == "Laptop"
def test_count_products_by_category():
    inventory = InventoryService()
    inventory.add_product(Product(1, "Laptop", 850000, 10, "Electronics"))
    inventory.add_product(Product(2, "Printer", 350000, 5, "Electronics"))
    inventory.add_product(Product(3, "Office Chair", 120000, 8, "Furniture"))
    result = inventory.count_products_by_category()
    assert result == {"Electronics": 2, "Furniture": 1,}
def test_total_quantity_by_category():
    inventory = InventoryService()
    inventory.add_product(Product(1, "Laptop", 850000, 10, "Electronics"))
    inventory.add_product(Product(2, "Printer", 350000, 5, "Electronics"))
    inventory.add_product(Product(3, "Office Chair", 120000, 8, "Furniture"))
    result = inventory.total_quantity_by_category()
    assert result == {"Electronics": 15, "Furniture": 8,}
def test_total_value_by_category():
    inventory = InventoryService()
    inventory.add_product(Product(1, "Laptop", 850000, 2, "Electronics"))
    inventory.add_product(Product(2, "Printer", 350000, 3, "Electronics"))
    inventory.add_product(Product(3, "Office Chair", 120000, 4, "Furniture"))
    result = inventory.total_value_by_category()
    assert result == {"Electronics": 2750000, "Furniture": 480000,}
def test_get_category_summary():
    inventory = InventoryService()
    inventory.add_product(Product(1, "Laptop", 850000, 2, "Electronics"))
    inventory.add_product(Product(2, "Printer", 350000, 3, "Electronics"))
    inventory.add_product(Product(3, "Office Chair", 120000, 4, "Furniture"))
    result = inventory.get_category_summary()
    assert result == {"Electronics": {"product_count": 2, "total_quantity": 5, "total_value": 2750000,}, "Furniture": {"product_count": 1, "total_quantity": 4, "total_value": 480000,},}
def test_category_summary_updates_after_stock_change():
    inventory = InventoryService()
    inventory.add_product(Product(1, "Laptop", 850000, 10, "Electronics"))
    inventory.add_product(Product(2, "Printer", 350000, 5, "Electronics"))
    inventory.stock_out(1, 2)
    inventory.stock_in(2, 3)
    result = inventory.get_category_summary()
    assert result == {"Electronics": {"product_count": 2, "total_quantity": 16, "total_value": 9600000,}}
def test_category_summary_after_removing_last_product():
    inventory = InventoryService()
    inventory.add_product(Product(1, "Laptop", 850000, 10, "Electronics"))
    inventory.add_product(Product(2, "Office Chair", 120000, 5, "Furniture"))
    inventory.remove_product(1)
    result = inventory.get_category_summary()
    assert result == {"Furniture": {"product_count": 1, "total_quantity": 5, "total_value": 600000,}}
def test_category_summary_empty_inventory():
    inventory = InventoryService()
    result = inventory.get_category_summary()
    assert result == {}
def test_search_products_by_name_or_category():
    inventory = InventoryService()
    inventory.add_product(Product(1, "Laptop", 850000, 10, "Electronics"))
    inventory.add_product(Product(2, "Office Chair", 120000, 5, "Furniture"))
    inventory.add_product(Product(3, "Printer", 350000, 8, "Electronics"))
    result = inventory.search_products("electronics")
    assert result == [inventory.get_product(1), inventory.get_product(3),]
def test_search_products_by_partial_category():
    inventory = InventoryService()
    inventory.add_product(Product(1, "Laptop", 850000, 10, "Electronics"))
    inventory.add_product(Product(2, "Printer", 350000, 5, "Electronics"))
    inventory.add_product(Product(3, "Office Chair", 120000, 8, "Furniture"))
    result = inventory.search_products("elect")
    assert len(result) == 2
    assert result[0].name == "Laptop"
    assert result[1].name == "Printer"
def test_search_products_does_not_return_duplicates():
    inventory = InventoryService()
    inventory.add_product(Product(1, "Electronics Guide", 5000, 10, "Electronics"))
    result = inventory.search_products("electronics")
    assert len(result) == 1
    assert result[0].name == "Electronics Guide"
def test_category_summary_groups_categories_case_insensitively():
    inventory = InventoryService()
    inventory.add_product(Product(1, "Laptop", 850000, 2, "Electronics"))
    inventory.add_product(Product(2, "Mouse", 15000, 5, "electronics"))
    inventory.add_product(Product(3, "Keyboard", 30000, 3, "ELECTRONICS"))
    result = inventory.get_category_summary()
    assert len(result) == 1
    assert result["Electronics"]["product_count"] == 3
    assert result["Electronics"]["total_quantity"] == 10
    assert result["Electronics"]["total_value"] == 1865000
def test_product_rejects_empty_category():
    with pytest.raises(ValueError, match="Category cannot be empty"):
        Product(1, "Laptop", 850000, 10, "")
def test_product_rejects_empty_name():
    with pytest.raises(ValueError, match="Product name cannot be empty"):
        Product(1, "", 850000, 10, "Electronics")
def test_product_rejects_whitespace_name():
    with pytest.raises(ValueError, match="Product name cannot be empty"):
        Product(1, "     ", 850000, 10, "Electronics")
def test_product_name_is_trimmed():
    product = Product(1, "   Laptop   ", 850000, 10, "Electronics")
    assert product.name == "Laptop"
def test_product_category_is_trimmed():
    product = Product(1, "Laptop", 850000, 10, "   Electronics   ")
    assert product.category == "Electronics"
def test_product_category_is_normalized():
    product = Product(1, "Laptop", 850000, 10, "electronics")
    assert product.category == "Electronics"
def test_product_name_is_normalized():
    product = Product(1, "laptop", 850000, 10, "Electronics")
    assert product.name == "Laptop"
def test_product_rejects_non_positive_id():
    with pytest.raises(ValueError, match="Product ID must be greater than zero"):
        Product(0, "Laptop", 850000, 10, "Electronics")
def test_product_rejects_negative_id():
    with pytest.raises(ValueError, match="Product ID must be greater than zero"):
        Product(-1, "Laptop", 850000, 10, "Electronics")
def test_product_rejects_non_integer_id():
    with pytest.raises(ValueError, match="Product ID must be an integer"):
        Product("ABC", "Laptop", 850000, 10, "Electronics")
def test_product_rejects_non_numeric_price():
    with pytest.raises(ValueError, match="Price must be a number"):
        Product(1, "Laptop", "850000", 10, "Electronics")
def test_product_rejects_boolean_price():
    with pytest.raises(ValueError, match="Price must be a number"):
        Product(1, "Laptop", True, 10, "Electronics")
def test_product_rejects_non_integer_quantity():
    with pytest.raises(ValueError, match="Quantity must be an integer"):
        Product(1, "Laptop", 850000, "10", "Electronics")
def test_product_rejects_boolean_quantity():
    with pytest.raises(ValueError, match="Quantity must be an integer"):
        Product(1, "Laptop", 850000, True, "Electronics")
def test_product_rejects_boolean_id():
    with pytest.raises(ValueError, match="Product ID must be an integer"):
        Product(True, "Laptop", 850000, 10, "Electronics")
def test_product_rejects_float_id():
    with pytest.raises(ValueError, match="Product ID must be an integer"):
        Product(1.5, "Laptop", 850000, 10, "Electronics")
def test_product_rejects_float_quantity():
    with pytest.raises(ValueError, match="Quantity must be an integer"):
        Product(1, "Laptop", 850000, 10.5, "Electronics")
def test_product_rejects_none_price():
    with pytest.raises(ValueError, match="Price must be a number"):
        Product(1, "Laptop", None, 10, "Electronics")
def test_product_rejects_none_quantity():
    with pytest.raises(ValueError, match="Quantity must be an integer"):
        Product(1, "Laptop", 850000, None, "Electronics")
def test_product_rejects_none_id():
    with pytest.raises(ValueError, match="Product ID must be an integer"):
        Product(None, "Laptop", 850000, 10, "Electronics")
def test_product_price_is_numeric():
    product = Product(1, "Laptop", 850000, 10, "Electronics")
    assert isinstance(product.price, (int, float))
def test_product_quantity_is_integer():
    product = Product(1, "Laptop", 850000, 10, "Electronics")
    assert isinstance(product.quantity, int)
def test_stock_in_rejects_non_integer_quantity():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 10, "Electronics")
    inventory.add_product(product)
    with pytest.raises(ValueError, match="Stock-in quantity must be an integer"):
        inventory.stock_in(1, 2.5)
def test_stock_out_rejects_non_integer_quantity():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 10, "Electronics")
    inventory.add_product(product)
    with pytest.raises(ValueError, match="Stock-out quantity must be an integer"):
        inventory.stock_out(1, 2.5)
def test_stock_out_rejects_boolean_quantity():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 10, "Electronics")
    inventory.add_product(product)
    with pytest.raises(ValueError, match="Stock-out quantity must be an integer"):
        inventory.stock_out(1, True)
def test_stock_in_rejects_non_integer_product_id():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 10, "Electronics")
    inventory.add_product(product)
    with pytest.raises(ValueError, match="Product ID must be an integer"):
        inventory.stock_in("1", 5)
def test_stock_out_rejects_non_integer_product_id():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 10, "Electronics")
    inventory.add_product(product)
    with pytest.raises(ValueError, match="Product ID must be an integer"):
        inventory.stock_out("1", 5)
def test_stock_in_invalid_quantity_does_not_change_inventory():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 10, "Electronics")
    inventory.add_product(product)
    with pytest.raises(ValueError, match="Stock-in quantity must be greater than zero"):
        inventory.stock_in(1, 0)
    assert product.quantity == 10
def test_stock_out_invalid_quantity_does_not_change_inventory():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 10, "Electronics")
    inventory.add_product(product)
    with pytest.raises(ValueError, match="Stock-out quantity must be greater than zero"):
        inventory.stock_out(1, 0)
    assert product.quantity == 10
def test_stock_in_negative_quantity_does_not_change_inventory():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 10, "Electronics")
    inventory.add_product(product)
    with pytest.raises(ValueError, match="Stock-in quantity must be greater than zero"):
        inventory.stock_in(1, -5)
    assert product.quantity == 10
def test_stock_out_negative_quantity_does_not_change_inventory():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 10, "Electronics")
    inventory.add_product(product)
    with pytest.raises(ValueError, match="Stock-out quantity must be greater than zero"):
        inventory.stock_out(1, -5)
    assert product.quantity == 10
def test_stock_in_records_transaction():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 10, "Electronics")
    inventory.add_product(product)
    inventory.stock_in(1, 5)
    transactions = inventory.get_transactions()
    assert len(transactions) == 1
    assert transactions[0]["product_id"] == 1
    assert transactions[0]["product_name"] == "Laptop"
    assert transactions[0]["type"] == "STOCK-IN"
    assert transactions[0]["quantity"] == 5
    assert transactions[0]["total_value"] == 4_250_000
def test_invalid_stock_in_does_not_create_transaction():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 10, "Electronics")
    inventory.add_product(product)
    with pytest.raises(ValueError, match="Stock-in quantity must be greater than zero"):
        inventory.stock_in(1, 0)
    assert inventory.get_transactions() == []
def test_invalid_stock_out_does_not_create_transaction():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 10, "Electronics")
    inventory.add_product(product)
    with pytest.raises(ValueError, match="Stock-out quantity must be greater than zero"):
        inventory.stock_out(1, 0)
    assert inventory.get_transactions() == []
def test_failed_stock_out_does_not_create_transaction():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 10, "Electronics")
    inventory.add_product(product)
    with pytest.raises(ValueError, match="Quantity cannot be negative"):
        inventory.stock_out(1, 15)
    assert product.quantity == 10
    assert inventory.get_transactions() == []
def test_multiple_stock_in_transactions_are_recorded():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 10, "Electronics")
    inventory.add_product(product)
    inventory.stock_in(1, 5)
    inventory.stock_in(1, 3)
    transactions = inventory.get_transactions()
    assert len(transactions) == 2
    assert transactions[0]["quantity"] == 5
    assert transactions[1]["quantity"] == 3
    assert product.quantity == 18
def test_multiple_stock_out_transactions_are_recorded():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 20, "Electronics")
    inventory.add_product(product)
    inventory.stock_out(1, 5)
    inventory.stock_out(1, 3)
    transactions = inventory.get_transactions()
    assert len(transactions) == 2
    assert transactions[0]["quantity"] == 5
    assert transactions[1]["quantity"] == 3
    assert product.quantity == 12
def test_multiple_stock_outs_update_quantity():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 20, "Electronics")
    inventory.add_product(product)
    inventory.stock_out(1, 5)
    inventory.stock_out(1, 3)
    assert product.quantity == 12
def test_transaction_history_records_mixed_stock_movements():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 20, "Electronics")
    inventory.add_product(product)
    inventory.stock_in(1, 5)
    inventory.stock_out(1, 3)
    transactions = inventory.get_transactions()
    assert len(transactions) == 2
    assert transactions[0]["type"] == "STOCK-IN"
    assert transactions[1]["type"] == "STOCK-OUT"
def test_transaction_history_returns_copy():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 20, "Electronics")
    inventory.add_product(product)
    inventory.stock_in(1, 5)
    transactions = inventory.get_transactions()
    transactions.clear()
    assert len(inventory.get_transactions()) == 1
def test_remove_product_preserves_transaction_history():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 20, "Electronics")
    inventory.add_product(product)
    inventory.stock_in(1, 5)
    inventory.remove_product(1)
    transactions = inventory.get_transactions()
    assert len(transactions) == 1
    assert transactions[0]["product_id"] == 1
    assert transactions[0]["type"] == "STOCK-IN"
def test_remove_product_does_not_affect_other_products():
    inventory = InventoryService()
    product1 = Product(1, "Laptop", 850000, 20, "Electronics")
    product2 = Product(2, "Mouse", 15000, 50, "Accessories")
    inventory.add_product(product1)
    inventory.add_product(product2)
    inventory.remove_product(1)
    products = inventory.get_all_products()
    assert len(products) == 1
    assert products[0].product_id == 2
    assert products[0].quantity == 50
def test_remove_product_updates_total_inventory_value():
    inventory = InventoryService()
    product1 = Product(1, "Laptop", 850000, 2, "Electronics")
    product2 = Product(2, "Mouse", 15000, 10, "Accessories")
    inventory.add_product(product1)
    inventory.add_product(product2)
    inventory.remove_product(1)
    assert inventory.calculate_total_value() == 150000
def test_remove_last_product_makes_inventory_value_zero():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 2, "Electronics")
    inventory.add_product(product)
    inventory.remove_product(1)
    assert inventory.calculate_total_value() == 0
def test_remove_last_product_updates_inventory_summary():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 2, "Electronics")
    inventory.add_product(product)
    inventory.remove_product(1)
    summary = inventory.get_inventory_summary()
    assert summary["total_products"] == 0
    assert summary["total_quantity"] == 0
    assert summary["total_value"] == 0
    assert summary["low_stock_count"] == 0
    assert summary["out_of_stock_count"] == 0
def test_remove_product_preserves_other_transaction_history():
    inventory = InventoryService()
    product1 = Product(1, "Laptop", 850000, 20, "Electronics")
    product2 = Product(2, "Mouse", 15000, 50, "Accessories")
    inventory.add_product(product1)
    inventory.add_product(product2)
    inventory.stock_in(1, 5)
    inventory.stock_out(2, 3)
    inventory.remove_product(1)
    transactions = inventory.get_transactions()
    assert len(transactions) == 2
def test_remove_product_preserves_transaction_types_for_multiple_products():
    inventory = InventoryService()
    product1 = Product(1, "Laptop", 850000, 20, "Electronics")
    product2 = Product(2, "Mouse", 15000, 50, "Accessories")
    inventory.add_product(product1)
    inventory.add_product(product2)
    inventory.stock_in(1, 5)
    inventory.stock_out(2, 3)
    inventory.remove_product(1)
    transactions = inventory.get_transactions()
    assert transactions[0]["type"] == "STOCK-IN"
    assert transactions[1]["type"] == "STOCK-OUT"
def test_stock_in_updates_inventory_summary():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 10, "Electronics")
    inventory.add_product(product)
    inventory.stock_in(1, 5)
    summary = inventory.get_inventory_summary()
    assert summary["total_quantity"] == 15
    assert summary["total_value"] == 12_750_000
def test_stock_out_updates_inventory_summary():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 10, "Electronics")
    inventory.add_product(product)
    inventory.stock_out(1, 3)
    summary = inventory.get_inventory_summary()
    assert summary["total_quantity"] == 7
    assert summary["total_value"] == 5_950_000
def test_stock_out_to_zero_updates_inventory_summary():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 5, "Electronics")
    inventory.add_product(product)
    inventory.stock_out(1, 5)
    summary = inventory.get_inventory_summary()
    assert summary["total_quantity"] == 0
    assert summary["total_value"] == 0
    assert summary["out_of_stock_count"] == 1
def test_stock_in_updates_product_stock_status():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 3, "Electronics")
    inventory.add_product(product)
    assert inventory.get_product_stock_status(1) == "LOW STOCK"
    inventory.stock_in(1, 5)
    assert inventory.get_product_stock_status(1) == "IN STOCK"
def test_stock_out_updates_product_stock_status():
    inventory = InventoryService()
    product = Product(1, "Laptop", 10, 10, "Electronics")
    inventory.add_product(product)
    assert inventory.get_product_stock_status(1) == "IN STOCK"
    inventory.stock_out(1, 6)
    assert inventory.get_product_stock_status(1) == "LOW STOCK"
def test_stock_out_changes_low_stock_to_out_of_stock():
    inventory = InventoryService()
    product = Product(1, "Laptop", 3, 3, "Electronics")
    inventory.add_product(product)
    assert inventory.get_product_stock_status(1) == "LOW STOCK"
    inventory.stock_out(1, 3)
    assert inventory.get_product_stock_status(1) == "OUT OF STOCK"
def test_stock_in_changes_out_of_stock_to_in_stock():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 0, "Electronics")
    inventory.add_product(product)
    assert inventory.get_product_stock_status(1) == "OUT OF STOCK"
    inventory.stock_in(1, 10)
    assert inventory.get_product_stock_status(1) == "IN STOCK"    
def test_low_stock_products_update_after_stock_change():
    inventory = InventoryService()
    product = Product(1, "Laptop", 3, 3, "Electronics")
    inventory.add_product(product)
    assert inventory.get_low_stock_products(5) == [product]
    inventory.stock_in(1, 5)
    assert inventory.get_low_stock_products(5) == []
def test_product_becomes_low_stock_after_stock_out():
    inventory = InventoryService()
    product = Product(1, "Laptop", 10, 10, "Electronics")
    inventory.add_product(product)
    assert inventory.get_low_stock_products(5) == []
    inventory.stock_out(1, 6)
    assert inventory.get_low_stock_products(5) == [product]
def test_out_of_stock_products_update_after_stock_in():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 0, "Electronics")
    inventory.add_product(product)
    assert inventory.get_out_of_stock_products() == [product]
    inventory.stock_in(1, 5)
    assert inventory.get_out_of_stock_products() == []
def test_product_becomes_out_of_stock_after_stock_out():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 5, "Electronics")
    inventory.add_product(product)
    assert inventory.get_out_of_stock_products() == []
    inventory.stock_out(1, 5)
    assert inventory.get_out_of_stock_products() == [product]
def test_inventory_summary_low_stock_count_updates_after_stock_in():
    inventory = InventoryService()
    product = Product(1, "Laptop", 3, 3, "Electronics")
    inventory.add_product(product)
    summary = inventory.get_inventory_summary()
    assert summary["low_stock_count"] == 1
    inventory.stock_in(1, 5)
    summary = inventory.get_inventory_summary()
    assert summary["low_stock_count"] == 0
def test_inventory_summary_low_stock_count_updates_after_stock_out():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 10, "Electronics")
    inventory.add_product(product)
    summary = inventory.get_inventory_summary()
    assert summary["low_stock_count"] == 0
    inventory.stock_out(1, 6)
    summary = inventory.get_inventory_summary()
    assert summary["low_stock_count"] == 1
def test_inventory_summary_out_of_stock_count_updates_after_stock_out():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 5, "Electronics")
    inventory.add_product(product)
    summary = inventory.get_inventory_summary()
    assert summary["out_of_stock_count"] == 0
    inventory.stock_out(1, 5)
    summary = inventory.get_inventory_summary()
    assert summary["out_of_stock_count"] == 1
def test_inventory_summary_out_of_stock_count_updates_after_stock_in():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 0, "Electronics")
    inventory.add_product(product)
    summary = inventory.get_inventory_summary()
    assert summary["out_of_stock_count"] == 1
    inventory.stock_in(1, 5)
    summary = inventory.get_inventory_summary()
    assert summary["out_of_stock_count"] == 0
def test_inventory_summary_separates_low_stock_and_out_of_stock():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 0, "Electronics")
    inventory.add_product(product)
    summary = inventory.get_inventory_summary()
    assert summary["out_of_stock_count"] == 1
    assert summary["low_stock_count"] == 0
def test_inventory_summary_low_stock_count_excludes_out_of_stock():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 0, "Electronics")
    inventory.add_product(product)
    summary = inventory.get_inventory_summary()
    assert summary["low_stock_count"] == 0
    assert summary["out_of_stock_count"] == 1
def test_stock_out_leaves_correct_remaining_quantity():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 20, "Electronics")
    inventory.add_product(product)
    inventory.stock_out(1, 7)
    updated_product = inventory.get_product(1)
    assert updated_product.quantity == 13
def test_stock_in_leaves_correct_updated_quantity():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 20, "Electronics")
    inventory.add_product(product)
    inventory.stock_in(1, 7)
    updated_product = inventory.get_product(1)
    assert updated_product.quantity == 27
def test_failed_stock_out_preserves_original_quantity():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 10, "Electronics")
    inventory.add_product(product)
    with pytest.raises(ValueError):
        inventory.stock_out(1, 15)
    updated_product = inventory.get_product(1)
    assert updated_product.quantity == 10
def test_failed_stock_out_preserves_transaction_history():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 10, "Electronics")
    inventory.add_product(product)
    inventory.stock_in(1, 5)
    transactions_before = inventory.get_transactions()
    with pytest.raises(ValueError):
        inventory.stock_out(1, 20)
    transactions_after = inventory.get_transactions()
    assert transactions_after == transactions_before
def test_stock_in_records_correct_transaction_total_value():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 10, "Electronics")
    inventory.add_product(product)
    inventory.stock_in(1, 4)
    transaction = inventory.get_transactions()[-1]
    assert transaction["total_value"] == 3400000
def test_stock_out_records_correct_transaction_total_value():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 10, "Electronics")
    inventory.add_product(product)
    inventory.stock_out(1, 4)
    transaction = inventory.get_transactions()[-1]
    assert transaction["total_value"] == 3400000
def test_search_products_ignores_surrounding_spaces():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 10, "Electronics")
    inventory.add_product(product)
    results = inventory.search_products("  laptop  ")
    assert len(results) == 1
    assert results[0].name == "Laptop"
def test_search_products_returns_empty_list_when_no_match():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 10, "Electronics")
    inventory.add_product(product)
    results = inventory.search_products("Phone")
    assert results == []
def test_remove_product_updates_inventory_summary():
    inventory = InventoryService()
    product1 = Product(1, "Laptop", 850000, 5, "Electronics")
    product2 = Product(2, "Mouse", 25000, 10, "Accessories")
    inventory.add_product(product1)
    inventory.add_product(product2)
    inventory.remove_product(1)
    summary = inventory.get_inventory_summary()
    assert summary["total_products"] == 1
    assert summary["total_quantity"] == 10
    assert summary["total_value"] == 250000
def test_remove_product_preserves_its_transaction_history():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 10, "Electronics")
    inventory.add_product(product)
    inventory.stock_in(1, 5)
    inventory.stock_out(1, 3)
    inventory.remove_product(1)
    transactions = inventory.get_transactions()
    assert len(transactions) == 2
    assert transactions[0]["product_id"] == 1
    assert transactions[1]["product_id"] == 1
def test_remove_product_preserves_transaction_types():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 10, "Electronics")
    inventory.add_product(product)
    inventory.stock_in(1, 5)
    inventory.stock_out(1, 3)
    inventory.remove_product(1)
    transactions = inventory.get_transactions()
    assert transactions[0]["type"] == "STOCK-IN"
    assert transactions[1]["type"] == "STOCK-OUT"
def test_inventory_transaction_persistence(tmp_path):
    file_path = tmp_path / "inventory.json"
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 10)
    inventory.add_product(product)
    inventory.stock_in(1, 5)
    inventory.save_inventory(file_path)
    loaded_inventory = InventoryService()
    loaded_inventory.load_inventory(file_path)
    transactions = loaded_inventory.get_transactions()
    assert len(transactions) == 1
    assert transactions[0]["product_id"] == 1
    assert transactions[0]["product_name"] == "Laptop"
    assert transactions[0]["type"] == "STOCK-IN"
    assert transactions[0]["quantity"] == 5
    assert transactions[0]["price"] == 850000
    assert transactions[0]["total_value"] == 4250000
def test_stock_transaction_records_timestamp():
    inventory = InventoryService()
    inventory.add_product(Product(1, "Laptop", 850000, 10, "Electronics"))
    inventory.stock_in(1, 5)
    transactions = inventory.get_transactions()
    assert len(transactions) == 1
    assert "timestamp" in transactions[0]
    assert transactions[0]["timestamp"]
def test_stock_out_transaction_records_timestamp():
    inventory = InventoryService()
    inventory.add_product(Product(1, "Laptop", 850000, 10, "Electronics"))
    inventory.stock_out(1, 3)
    transactions = inventory.get_transactions()
    assert len(transactions) == 1
    assert "timestamp" in transactions[0]
    assert transactions[0]["timestamp"]
def test_generate_inventory_report_contains_summary():
    inventory = InventoryService()
    inventory.add_product(Product(1, "Laptop", 850000, 5, "Electronics"))
    report = inventory.generate_inventory_report()
    assert "INVENTORY REPORT" in report
    assert "Total Products: 1" in report
    assert "Total Quantity: 5" in report
    assert "Total Inventory Value: ₦4,250,000.00" in report
def test_generate_inventory_report_contains_stock_status():
    inventory = InventoryService()
    inventory.add_product(Product(1, "Laptop", 850000, 3, "Electronics"))
    inventory.add_product(Product(2, "Mouse", 15000, 0, "Accessories"))
    report = inventory.generate_inventory_report()
    assert "Low Stock: 1" in report
    assert "Out of Stock: 1" in report
def test_generate_inventory_report_contains_category_summary():
    inventory = InventoryService()
    inventory.add_product(Product(1, "Laptop", 850000, 5, "Electronics"))
    inventory.add_product(Product(2, "Mouse", 15000, 10, "Accessories"))
    report = inventory.generate_inventory_report()
    assert "Categories:" in report
    assert "Electronics" in report
    assert "Products: 1" in report
    assert "Quantity: 5" in report
    assert "Value: ₦4,250,000.00" in report
    assert "Accessories" in report
def test_generate_inventory_report_empty_inventory():
    inventory = InventoryService()
    report = inventory.generate_inventory_report()
    assert "INVENTORY REPORT" in report
    assert "Total Products: 0" in report
    assert "Total Quantity: 0" in report
    assert "Total Inventory Value: ₦0.00" in report
    assert "Low Stock: 0" in report
    assert "Out of Stock: 0" in report
    assert "Categories:" in report
def test_generate_inventory_report_aggregates_category_data():
    inventory = InventoryService()
    inventory.add_product(Product(1, "Laptop", 850000, 5, "Electronics"))
    inventory.add_product(Product(2, "Monitor", 250000, 3, "Electronics"))
    report = inventory.generate_inventory_report()
    assert "Electronics" in report
    assert "Products: 2" in report
    assert "Quantity: 8" in report
    assert "Value: ₦5,000,000.00" in report
def test_stock_in_rejects_boolean_product_id():
    inventory = InventoryService()
    with pytest.raises(ValueError, match="Product ID must be an integer"):
        inventory.stock_in(True, 5)
def test_stock_out_rejects_boolean_product_id():
    inventory = InventoryService()
    with pytest.raises(ValueError, match="Product ID must be an integer"):
        inventory.stock_out(True, 5)
def test_stock_in_rejects_boolean_quantity():
    inventory = InventoryService()
    with pytest.raises(ValueError, match="Stock-in quantity must be an integer"):
        inventory.stock_in(1, True)
def test_search_products_by_category_returns_matching_products():
    inventory = InventoryService()
    inventory.add_product(Product(1, "Laptop", 850000, 5, "Electronics"))
    inventory.add_product(Product(2, "Chair", 150000, 10, "Furniture"))
    results = inventory.search_products_by_category("electronics")
    assert len(results) == 1
    assert results[0].name == "Laptop"
def test_get_category_summary_aggregates_products():
    inventory = InventoryService()
    inventory.add_product(Product(1, "Laptop", 850000, 5, "Electronics"))
    inventory.add_product(Product(2, "Phone", 500000, 3, "Electronics"))
    inventory.add_product(Product(3, "Chair", 150000, 4, "Furniture"))
    summary = inventory.get_category_summary()
    assert summary["Electronics"]["product_count"] == 2
    assert summary["Electronics"]["total_quantity"] == 8
    assert summary["Electronics"]["total_value"] == 5_750_000
    assert summary["Furniture"]["product_count"] == 1
    assert summary["Furniture"]["total_quantity"] == 4
    assert summary["Furniture"]["total_value"] == 600_000
def test_get_category_summary_normalizes_category_names():
    inventory = InventoryService()
    inventory.add_product(Product(1, "Laptop", 850000, 5, "electronics"))
    summary = inventory.get_category_summary()
    assert "Electronics" in summary
    assert "electronics" not in summary
def test_get_products_by_inventory_value():
    inventory = InventoryService()
    inventory.add_product(Product(1, "Laptop", 850000, 5, "Electronics"))
    inventory.add_product(Product(2, "Phone", 500000, 3, "Electronics"))
    inventory.add_product(Product(3, "Chair", 150000, 4, "Furniture"))
    results = inventory.get_products_by_inventory_value()
    assert results[0].name == "Laptop"
    assert results[1].name == "Phone"
    assert results[2].name == "Chair"
def test_get_products_by_inventory_value_empty_inventory():
    inventory = InventoryService()
    results = inventory.get_products_by_inventory_value()
    assert results == []
def test_get_products_by_inventory_value_preserves_order_for_equal_values():
    inventory = InventoryService()
    inventory.add_product(Product(1, "Laptop", 100000, 2, "Electronics"))
    inventory.add_product(Product(2, "Phone", 50000, 4, "Electronics"))
    results = inventory.get_products_by_inventory_value()
    assert results[0].name == "Laptop"
    assert results[1].name == "Phone"
def test_get_products_by_inventory_value_does_not_modify_original_order():
    inventory = InventoryService()
    inventory.add_product(Product(1, "Laptop", 850000, 1, "Electronics"))
    inventory.add_product(Product(2, "Phone", 500000, 5, "Electronics"))
    inventory.add_product(Product(3, "Chair", 150000, 2, "Furniture"))
    original_order = [product.name for product in inventory.products]
    inventory.get_products_by_inventory_value()
    current_order = [product.name for product in inventory.products]
    assert current_order == original_order
def test_get_products_by_inventory_value_uses_price_times_quantity():
    inventory = InventoryService()
    inventory.add_product(Product(1, "Laptop", 100000, 10, "Electronics"))
    inventory.add_product(Product(2, "Phone", 500000, 1, "Electronics"))
    inventory.add_product(Product(3, "Chair", 50000, 5, "Furniture"))
    results = inventory.get_products_by_inventory_value()
    assert results[0].name == "Laptop"
    assert results[1].name == "Phone"
    assert results[2].name == "Chair"
def test_get_top_products_by_inventory_value():
    inventory = InventoryService()
    inventory.add_product(Product(1, "Laptop", 850000, 5, "Electronics"))
    inventory.add_product(Product(2, "Phone", 500000, 3, "Electronics"))
    inventory.add_product(Product(3, "Chair", 150000, 4, "Furniture"))
    inventory.add_product(Product(4, "Desk", 300000, 2, "Furniture"))
    results = inventory.get_top_products_by_inventory_value(2)
    assert len(results) == 2
    assert results[0].name == "Laptop"
    assert results[1].name == "Phone"
def test_get_top_products_by_inventory_value_limit_larger_than_inventory():
    inventory = InventoryService()
    inventory.add_product(Product(1, "Laptop", 850000, 5, "Electronics"))
    inventory.add_product(Product(2, "Phone", 500000, 3, "Electronics"))
    inventory.add_product(Product(3, "Chair", 150000, 4, "Furniture"))
    results = inventory.get_top_products_by_inventory_value(10)
    assert len(results) == 3
    assert results[0].name == "Laptop"
    assert results[1].name == "Phone"
    assert results[2].name == "Chair"
def test_get_top_products_by_inventory_value_empty_inventory():
        inventory = InventoryService()
        results = inventory.get_top_products_by_inventory_value(5)
        assert results == []
def test_get_top_products_by_inventory_value_rejects_zero_limit():
    inventory = InventoryService()
    with pytest.raises(ValueError, match="Limit must be greater than zero"):
        inventory.get_top_products_by_inventory_value(0)
def test_get_top_products_by_inventory_value_rejects_negative_limit():
    inventory = InventoryService()
    with pytest.raises(ValueError, match="Limit must be greater than zero"):
        inventory.get_top_products_by_inventory_value(-3)
def test_get_top_products_by_inventory_value_rejects_non_integer_limit():
    inventory = InventoryService()
    with pytest.raises(ValueError, match="Limit must be an integer"):
        inventory.get_top_products_by_inventory_value(2.5)
def test_get_top_products_by_inventory_value_rejects_boolean_limit():
    inventory = InventoryService()
    with pytest.raises(ValueError, match="Limit must be an integer"):
        inventory.get_top_products_by_inventory_value(True)
def test_get_categories_by_inventory_value():
    inventory = InventoryService()
    inventory.add_product(Product(1, "Laptop", 850000, 2, "Electronics"))
    inventory.add_product(Product(2, "Phone", 500000, 3, "Electronics"))
    inventory.add_product(Product(3, "Chair", 100000, 5, "Furniture"))
    result = inventory.get_categories_by_inventory_value()
    assert result == [("Electronics", 3200000), ("Furniture", 500000),]
def test_get_categories_by_inventory_value_empty_inventory():
    inventory = InventoryService()
    result = inventory.get_categories_by_inventory_value()
    assert result == []
def test_get_categories_by_inventory_value_preserves_order_for_equal_values():
    inventory = InventoryService()
    inventory.add_product(Product(1, "Laptop", 500000, 2, "Electronics"))
    inventory.add_product(Product(2, "Chair", 250000, 4, "Furniture"))
    result = inventory.get_categories_by_inventory_value()
    assert result == [("Electronics", 1000000), ("Furniture", 1000000),]
def test_get_categories_by_inventory_value_uses_price_times_quantity():
    inventory = InventoryService()
    inventory.add_product(Product(1, "Laptop", 800000, 3, "Electronics"))
    inventory.add_product(Product(2, "Mouse", 20000, 5, "Electronics"))
    inventory.add_product(Product(3, "Chair", 100000, 2, "Furniture"))
    result = inventory.get_categories_by_inventory_value()
    assert result == [("Electronics", 2500000), ("Furniture", 200000)]
def test_get_categories_by_inventory_value_does_not_modify_products():
    inventory = InventoryService()
    product1 = Product(1, "Laptop", 500000, 2, "Electronics")
    product2 = Product(2, "Chair", 100000, 10, "Furniture")
    inventory.add_product(product1)
    inventory.add_product(product2)
    original_products = inventory.get_all_products()
    inventory.get_categories_by_inventory_value()
    assert inventory.get_all_products() == original_products
def test_get_low_stock_percentage():
    inventory = InventoryService()
    inventory.add_product(Product(1, "Laptop", 850000, 2, "Electronics"))
    inventory.add_product(Product(2, "Phone", 500000, 10, "Electronics"))
    inventory.add_product(Product(3, "Chair", 100000, 4, "Furniture"))
    inventory.add_product(Product(4, "Desk", 200000, 8, "Furniture"))
    result = inventory.get_low_stock_percentage()
    assert result == 50.0
def test_get_low_stock_percentage_empty_inventory():
    inventory = InventoryService()
    result = inventory.get_low_stock_percentage()
    assert result == 0.0
def test_get_low_stock_percentage_with_custom_threshold():
    inventory = InventoryService()
    inventory.add_product(Product(1, "Laptop", 850000, 2, "Electronics"))
    inventory.add_product(Product(2, "Phone", 500000, 5, "Electronics"))
    inventory.add_product(Product(3, "Chair", 100000, 8, "Furniture"))
    inventory.add_product(Product(4, "Desk", 200000, 10, "Furniture"))
    result = inventory.get_low_stock_percentage(low_stock_threshold=5)
    assert result == 50.0
def test_get_low_stock_percentage_rejects_negative_threshold():
        inventory = InventoryService()
        with pytest.raises(ValueError, match="Low stock threshold cannot be negative"):
            inventory.get_low_stock_percentage(low_stock_threshold=-1)
def test_get_low_stock_percentage_rejects_non_integer_threshold():
    inventory = InventoryService()
    with pytest.raises(ValueError, match="Low stock threshold must be an integer"):
        inventory.get_low_stock_percentage(low_stock_threshold=2.5)
def test_get_out_of_stock_percentage():
    inventory = InventoryService()
    inventory.add_product(Product(1, "Laptop", 850000, 0, "Electronics"))
    inventory.add_product(Product(2, "Phone", 500000, 10, "Electronics"))
    inventory.add_product(Product(3, "Chair", 100000, 0, "Furniture"))
    inventory.add_product(Product(4, "Desk", 200000, 8, "Furniture"))
    result = inventory.get_out_of_stock_percentage()
    assert result == 50.0
def test_get_out_of_stock_percentage_empty_inventory():
    inventory = InventoryService()
    result = inventory.get_out_of_stock_percentage()
    assert result == 0.0
def test_get_out_of_stock_percentage_counts_only_zero_quantity():
    inventory = InventoryService()
    inventory.add_product(Product(1, "Laptop", 850000, 0, "Electronics"))
    inventory.add_product(Product(2, "Phone", 500000, 1, "Electronics"))
    inventory.add_product(Product(3, "Chair", 100000, 0, "Furniture"))
    inventory.add_product(Product(4, "Desk", 200000, 5, "Furniture"))
    inventory.add_product(Product(5, "Mouse", 20000, 10, "Electronics"))
    result = inventory.get_out_of_stock_percentage()
    assert result == 40.0
def test_get_out_of_stock_percentage_returns_percentage_value():
    inventory = InventoryService()
    inventory.add_product(Product(1, "Laptop", 850000, 0, "Electronics"))
    inventory.add_product(Product(2, "Phone", 500000, 10, "Electronics"))
    result = inventory.get_out_of_stock_percentage()
    assert result == 50.0
    assert result != 0.5
def test_get_stock_health_score():
    inventory = InventoryService()
    inventory.add_product(Product(1, "Laptop", 850000, 10, "Electronics"))
    inventory.add_product(Product(2, "Phone", 500000, 5, "Electronics"))
    inventory.add_product(Product(3, "Chair", 100000, 0, "Furniture"))
    inventory.add_product(Product(4, "Desk", 200000, 8, "Furniture"))
    inventory.add_product(Product(5, "Mouse", 20000, 0, "Electronics"))
    result = inventory.get_stock_health_score()
    assert result == 60.0
def test_get_stock_health_score_empty_inventory():
        inventory = InventoryService()
        result = inventory.get_stock_health_score()
        assert result == 0.0
def test_get_stock_health_score_all_products_in_stock():
    inventory = InventoryService()
    inventory.add_product(Product(1, "Laptop", 850000, 10, "Electronics"))
    inventory.add_product(Product(2, "Phone", 500000, 5, "Electronics"))
    inventory.add_product(Product(3, "Chair", 100000, 8, "Furniture"))
    result = inventory.get_stock_health_score()
    assert result == 100.0
def test_get_stock_health_score_all_products_out_of_stock():
    inventory = InventoryService()
    inventory.add_product(Product(1, "Laptop", 850000, 0, "Electronics"))
    inventory.add_product(Product(2, "Phone", 500000, 0, "Electronics"))
    inventory.add_product(Product(3, "Chair", 100000, 0, "Furniture"))
    result = inventory.get_stock_health_score()
    assert result == 0.0
def test_get_stock_health_score_returns_percentage_value():
    inventory = InventoryService()
    inventory.add_product(Product(1, "Laptop", 850000, 10, "Electronics"))
    inventory.add_product(Product(2, "Phone", 500000, 0, "Electronics"))
    result = inventory.get_stock_health_score()
    assert result == 50.0
    assert result != 0.5
def test_get_stock_status_counts():
    inventory = InventoryService()
    inventory.add_product(Product(1, "Laptop", 850000, 10, "Electronics"))
    inventory.add_product(Product(2, "Phone", 500000, 3, "Electronics"))
    inventory.add_product(Product(3, "Chair", 100000, 0, "Furniture"))
    inventory.add_product(Product(4, "Desk", 200000, 8, "Furniture"))
    inventory.add_product(Product(5, "Mouse", 20000, 2, "Electronics"))
    result = inventory.get_stock_status_counts()
    assert result == {"in_stock": 2, "low_stock": 2, "out_of_stock": 1,}
def test_get_stock_status_counts_empty_inventory():
    inventory = InventoryService()
    result = inventory.get_stock_status_counts()
    assert result == {"in_stock": 0, "low_stock": 0, "out_of_stock": 0,}
def test_get_stock_status_counts_with_custom_threshold():
    inventory = InventoryService()
    inventory.add_product(Product(1, "Laptop", 850000, 10, "Electronics"))
    inventory.add_product(Product(2, "Phone", 500000, 6, "Electronics"))
    inventory.add_product(Product(3, "Chair", 100000, 3, "Furniture"))
    inventory.add_product(Product(4, "Desk", 200000, 0, "Furniture"))
    result = inventory.get_stock_status_counts(low_stock_threshold=6)
    assert result == {"in_stock": 1, "low_stock": 2, "out_of_stock": 1,}
def test_get_stock_status_counts_rejects_negative_threshold():
    inventory = InventoryService()
    with pytest.raises(ValueError, match="Low stock threshold cannot be negative"):
        inventory.get_stock_status_counts(low_stock_threshold=-1)
def test_get_stock_status_counts_rejects_non_integer_threshold():
    inventory = InventoryService()
    with pytest.raises(ValueError, match="Low stock threshold must be an integer"):
        inventory.get_stock_status_counts(low_stock_threshold=5.5)
def test_get_inventory_value_percentage():
    inventory = InventoryService()
    inventory.add_product(Product(1, "Laptop", 800000, 1, "Electronics"))
    inventory.add_product(Product(2, "Phone", 200000, 1, "Electronics"))
    result = inventory.get_inventory_value_percentage()
    assert result == {"Laptop": 80.0, "Phone": 20.0,}
def test_get_inventory_value_percentage_empty_inventory():
    inventory = InventoryService()
    result = inventory.get_inventory_value_percentage()
    assert result == {}
def test_get_inventory_value_percentage_zero_inventory_value():
    inventory = InventoryService()
    inventory.add_product(Product(1, "Free Item", 0, 10, "General"))
    inventory.add_product(Product(2, "Another Item", 0, 5, "General"))
    result = inventory.get_inventory_value_percentage()
    assert result == {"Free Item": 0.0, "Another Item": 0.0,}
def test_get_inventory_value_percentage_totals_100():
    inventory = InventoryService()
    inventory.add_product(Product(1, "Laptop", 800000, 2, "Electronics"))
    inventory.add_product(Product(2, "Phone", 200000, 2, "Electronics"))
    inventory.add_product(Product(3, "Chair", 100000, 2, "Furniture"))
    result = inventory.get_inventory_value_percentage()
    assert sum(result.values()) == 100.0
def test_get_dashboard_data():
    inventory = InventoryService()
    inventory.add_product(Product(1, "Laptop", 800000, 10, "Electronics"))
    inventory.add_product(Product(2, "Phone", 200000, 3, "Electronics"))
    inventory.add_product(Product(3, "Chair", 100000, 0, "Furniture"))
    result = inventory.get_dashboard_data()
    assert result == {"total_products": 3, "total_quantity": 13, "total_value": 8600000, "in_stock": 1, "low_stock": 1, "out_of_stock": 1, "stock_health": 66.66666666666666, "top_product": "Laptop", "category_values": { "Electronics": 8600000, "Furniture": 0,}, "top_category": "Electronics", "attention_products": ["Phone", "Chair"], "inventory_value_percentage": {"Laptop": 93.02, "Phone": 6.98, "Chair": 0.0,}, "top_products_by_value": ["Laptop", "Phone", "Chair"], "top_products_with_values": [ {"name": "Laptop", "value": 8000000}, {"name": "Phone", "value": 600000}, {"name": "Chair", "value": 0},], "attention_count": 2,}   
def test_get_dashboard_data_empty_inventory():
    inventory = InventoryService()
    result = inventory.get_dashboard_data()
    assert result == {"total_products": 0, "total_quantity": 0, "total_value": 0, "in_stock": 0, "low_stock": 0, "out_of_stock": 0, "stock_health": 0.0, "top_product": None, "category_values": {}, "category_values": {}, "attention_products": [], "inventory_value_percentage": {}, "top_products_by_value": [], "top_products_with_values": [], "attention_count": 0,
"top_category": None,}
def test_get_dashboard_data_includes_stock_health():
    inventory = InventoryService()
    inventory.add_product(Product(1, "Laptop", 800000, 10, "Electronics"))
    inventory.add_product(Product(2, "Phone", 200000, 0, "Electronics"))
    result = inventory.get_dashboard_data()
    assert result["stock_health"] == 50.0
def test_get_dashboard_data_includes_top_product():
    inventory = InventoryService()
    inventory.add_product(Product(1, "Laptop", 800000, 10, "Electronics"))
    inventory.add_product(Product(2, "Phone", 200000, 3, "Electronics"))
    inventory.add_product(Product(3, "Chair", 100000, 5, "Furniture"))
    result = inventory.get_dashboard_data()
    assert result["top_product"] == "Laptop"
def test_get_dashboard_data_empty_inventory_top_product():
    inventory = InventoryService()
    result = inventory.get_dashboard_data()
    assert result["top_product"] is None
def test_get_dashboard_category_values():
    inventory = InventoryService()
    inventory.add_product(Product(1, "Laptop", 850000, 5, "Electronics"))
    inventory.add_product(Product(2, "Phone", 500000, 4, "Electronics"))
    inventory.add_product(Product(3, "Chair", 100000, 10, "Furniture"))
    dashboard = inventory.get_dashboard_data()
    assert dashboard["category_values"] == {"Electronics": 6250000, "Furniture": 1000000,}
def test_get_dashboard_top_category():
    inventory = InventoryService()
    inventory.add_product(Product(1, "Laptop", 850000, 5, "Electronics"))
    inventory.add_product(Product(2, "Phone", 500000, 4, "Electronics"))
    inventory.add_product(Product(3, "Chair", 100000, 10, "Furniture"))
    dashboard = inventory.get_dashboard_data()
    assert dashboard["top_category"] == "Electronics"
def test_get_dashboard_top_category_empty_inventory():
    inventory = InventoryService()
    dashboard = inventory.get_dashboard_data()
    assert dashboard["top_category"] is None
def test_get_dashboard_attention_products():
    inventory = InventoryService()
    inventory.add_product(Product(1, "Laptop", 850000, 0, "Electronics"))
    inventory.add_product(Product(2, "Phone", 500000, 3, "Electronics"))
    inventory.add_product(Product(3, "Chair", 100000, 10, "Furniture"))
    dashboard = inventory.get_dashboard_data()
    assert dashboard["attention_products"] == ["Laptop", "Phone",]
def test_get_dashboard_attention_products_custom_threshold():
    inventory = InventoryService()
    inventory.add_product(Product(1, "Laptop", 850000, 4, "Electronics"))
    inventory.add_product(Product(2, "Phone", 500000, 6, "Electronics"))
    inventory.add_product(Product(3, "Chair", 100000, 10, "Furniture"))
    dashboard = inventory.get_dashboard_data(low_stock_threshold=6)
    assert dashboard["attention_products"] == ["Laptop", "Phone",]
def test_get_dashboard_attention_products_negative_threshold():
    inventory = InventoryService()
    with pytest.raises(ValueError, match="Low stock threshold cannot be negative"):
        inventory.get_dashboard_data(low_stock_threshold=-1)
def test_get_dashboard_inventory_value_percentage():
    inventory = InventoryService()
    inventory.add_product(Product(1, "Laptop", 800000, 10, "Electronics"))
    inventory.add_product(Product(2, "Phone", 200000, 3, "Electronics"))
    inventory.add_product(Product(3, "Chair", 100000, 0, "Furniture"))
    dashboard = inventory.get_dashboard_data()
    assert dashboard["inventory_value_percentage"] == {"Laptop": 93.02, "Phone": 6.98, "Chair": 0.0,}
def test_get_dashboard_top_products_by_inventory_value():
    inventory = InventoryService()
    inventory.add_product(Product(1, "Laptop", 800000, 10, "Electronics"))
    inventory.add_product(Product(2, "Phone", 200000, 3, "Electronics"))
    inventory.add_product(Product(3, "Chair", 100000, 5, "Furniture"))
    dashboard = inventory.get_dashboard_data()
    assert dashboard["top_products_by_value"] == ["Laptop", "Phone", "Chair",]
def test_get_dashboard_top_products_with_inventory_values():
    inventory = InventoryService()
    inventory.add_product(Product(1, "Laptop", 800000, 10, "Electronics"))
    inventory.add_product(Product(2, "Phone", 200000, 3, "Electronics"))
    inventory.add_product(Product(3, "Chair", 100000, 5, "Furniture"))
    dashboard = inventory.get_dashboard_data()
    assert dashboard["top_products_with_values"] == [ {"name": "Laptop", "value": 8000000}, {"name": "Phone", "value": 600000}, {"name": "Chair", "value": 500000},]
def test_get_dashboard_data_uses_custom_low_stock_threshold():
    inventory = InventoryService()
    inventory.add_product(Product(1, "Laptop", 100000, 4))
    inventory.add_product(Product(2, "Phone", 50000, 6))
    dashboard = inventory.get_dashboard_data(low_stock_threshold=3)
    assert dashboard["low_stock"] == 0
    assert dashboard["in_stock"] == 2
def test_get_dashboard_data_includes_attention_count():
    inventory = InventoryService()
    inventory.add_product(Product(1, "Laptop", 100000, 0))
    inventory.add_product(Product(2, "Phone", 50000, 3))
    inventory.add_product(Product(3, "Chair", 30000, 10))
    dashboard = inventory.get_dashboard_data(low_stock_threshold=5)
    assert dashboard["attention_count"] == 2
def test_get_inventory_alerts():
    inventory = InventoryService()
    inventory.add_product(Product(1, "Laptop", 100000, 3))
    inventory.add_product(Product(2, "Phone", 50000, 0))
    inventory.add_product(Product(3, "Chair", 30000, 10))
    alerts = inventory.get_inventory_alerts()
    assert alerts == [{"product_id": 1, "product_name": "Laptop", "status": "LOW STOCK", "quantity": 3,}, {"product_id": 2, "product_name": "Phone", "status": "OUT OF STOCK", "quantity": 0,},]
def test_get_inventory_alerts_uses_custom_threshold():
    inventory = InventoryService()
    inventory.add_product(Product(1, "Laptop", 4_000_000, 4))
    inventory.add_product(Product(2, "Phone", 500_000, 6))
    inventory.add_product(Product(3, "Chair", 100_000, 8))
    alerts = inventory.get_inventory_alerts(low_stock_threshold=3)
    assert alerts == []
def test_get_inventory_alerts_rejects_negative_threshold():
    inventory = InventoryService()
    with pytest.raises(ValueError, match="Low stock threshold cannot be negative"):inventory.get_inventory_alerts(low_stock_threshold=-1)
def test_get_transaction_summary():
    inventory = InventoryService()
    inventory.add_product(Product(1, "Laptop", 100000, 10))
    inventory.stock_in(1, 5)
    inventory.stock_in(1, 10)
    inventory.stock_out(1, 3)
    summary = inventory.get_transaction_summary()
    assert summary == {"total_transactions": 3, "stock_in_transactions": 2, "stock_out_transactions": 1, "total_stock_in_quantity": 15, "total_stock_out_quantity": 3,}
def test_get_transaction_value_summary():
    inventory = InventoryService()
    inventory.add_product(Product(1, "Laptop", 100000, 10))
    inventory.stock_in(1, 5)
    inventory.stock_out(1, 2)
    summary = inventory.get_transaction_value_summary()
    assert summary == {"total_stock_in_value": 500000, "total_stock_out_value": 200000,}
def test_get_transaction_value_summary_multiple_products():
    inventory = InventoryService()
    inventory.add_product(Product(1, "Laptop", 100000, 10))
    inventory.add_product(Product(2, "Phone", 50000, 20))
    inventory.stock_in(1, 5)     # ₦500,000
    inventory.stock_out(1, 2)   # ₦200,000
    inventory.stock_in(2, 10)   # ₦500,000
    inventory.stock_out(2, 4)   # ₦200,000
    summary = inventory.get_transaction_value_summary()
    assert summary == {"total_stock_in_value": 1000000, "total_stock_out_value": 400000,}
def test_get_transaction_summary_repeated_transactions():
    inventory = InventoryService()
    inventory.add_product(Product(1, "Laptop", 100000, 20))
    inventory.stock_in(1, 5)
    inventory.stock_in(1, 10)
    inventory.stock_in(1, 7)
    inventory.stock_out(1, 3)
    inventory.stock_out(1, 4)
    summary = inventory.get_transaction_summary()
    assert summary == {"total_transactions": 5, "stock_in_transactions": 3, "stock_out_transactions": 2, "total_stock_in_quantity": 22, "total_stock_out_quantity": 7,}
def test_get_transaction_summary_multiple_products():
    inventory = InventoryService()
    inventory.add_product(Product(1, "Laptop", 100000, 10))
    inventory.add_product(Product(2, "Phone", 50000, 20))
    inventory.stock_in(1, 5)
    inventory.stock_out(1, 2)
    inventory.stock_in(2, 10)
    inventory.stock_out(2, 4)
    summary = inventory.get_transaction_summary()
    assert summary == {"total_transactions": 4, "stock_in_transactions": 2, "stock_out_transactions": 2, "total_stock_in_quantity": 15, "total_stock_out_quantity": 6,}
def test_get_transaction_summary_empty():
    inventory = InventoryService()
    summary = inventory.get_transaction_summary()
    assert summary == {"total_transactions": 0, "stock_in_transactions": 0, "stock_out_transactions": 0, "total_stock_in_quantity": 0, "total_stock_out_quantity": 0,}
def test_get_transaction_value_summary_empty():
    inventory = InventoryService()
    summary = inventory.get_transaction_value_summary()
    assert summary == {"total_stock_in_value": 0, "total_stock_out_value": 0,} 
def test_generate_inventory_report_contains_stock_movement():
    inventory = InventoryService()
    inventory.add_product(Product(1, "Laptop", 100000, 10, "Electronics"))
    inventory.stock_in(1, 5)
    inventory.stock_out(1, 2)
    report = inventory.generate_inventory_report()
    assert "Stock Movement:" in report
    assert "Stock-In Transactions: 1" in report
    assert "Stock-In Quantity: 5" in report
    assert "Stock-In Value: ₦500,000.00" in report
    assert "Stock-Out Transactions: 1" in report
    assert "Stock-Out Quantity: 2" in report
    assert "Stock-Out Value: ₦200,000.00" in report   
def test_generate_inventory_report_empty_stock_movement():
    inventory = InventoryService()
    inventory.add_product(Product(1, "Laptop", 100000, 10, "Electronics"))
    report = inventory.generate_inventory_report()
    assert "Stock Movement:" in report
    assert "Stock-In Transactions: 0" in report
    assert "Stock-In Quantity: 0" in report
    assert "Stock-In Value: ₦0.00" in report
    assert "Stock-Out Transactions: 0" in report
    assert "Stock-Out Quantity: 0" in report
    assert "Stock-Out Value: ₦0.00" in report
def test_save_inventory_report(tmp_path):
    inventory = InventoryService()
    inventory.add_product(Product(1, "Laptop", 850000, 5, "Electronics"))
    file_path = tmp_path / "inventory_report.txt"
    inventory.save_inventory_report(file_path)
    with open(file_path, "r", encoding="utf-8") as file:
        report = file.read()
    assert "INVENTORY REPORT" in report
    assert "Total Products: 1" in report
    assert "Total Quantity: 5" in report
    assert "Total Inventory Value: ₦4,250,000.00" in report
def test_save_inventory_report_requires_file_path():
    inventory = InventoryService()
    with pytest.raises(ValueError, match="File path cannot be empty"):
        inventory.save_inventory_report("")
def test_save_inventory_report_rejects_whitespace_file_path():
    inventory = InventoryService()
    with pytest.raises(ValueError, match="File path cannot be empty"):
        inventory.save_inventory_report("   ")
def test_generate_inventory_report_contains_generated_date():
    inventory = InventoryService()
    report = inventory.generate_inventory_report()
    assert "Report Generated:" in report
def test_generate_inventory_report_contains_formatted_generated_date():
    import re
    inventory = InventoryService()
    report = inventory.generate_inventory_report()
    match = re.search(r"Report Generated: \d{2} [A-Za-z]+ \d{4} \d{2}:\d{2}", report)
    assert match is not None
def test_generate_inventory_report_contains_low_stock_products():
    inventory = InventoryService()
    inventory.add_product(Product(1, "Laptop", 850000, 2, "Electronics"))
    inventory.add_product(Product(2, "Mouse", 15000, 10, "Electronics"))
    report = inventory.generate_inventory_report()
    assert "Low Stock Products:" in report
    assert "Laptop - Quantity: 2" in report
    assert "Mouse - Quantity: 10" not in report
def test_generate_inventory_report_with_no_low_stock_products():
    inventory = InventoryService()
    inventory.add_product(Product(1, "Laptop", 850000, 10, "Electronics"))
    report = inventory.generate_inventory_report()
    assert "Low Stock Products:" in report
    assert "Laptop - Quantity: 10" not in report
def test_generate_inventory_report_contains_out_of_stock_products():
    inventory = InventoryService()
    inventory.add_product(Product(1, "Printer", 120000, 0, "Electronics"))
    inventory.add_product(Product(2, "Monitor", 200000, 0, "Electronics"))
    inventory.add_product(Product(3, "Laptop", 850000, 5, "Electronics"))
    report = inventory.generate_inventory_report()
    assert "Out of Stock Products:" in report
    assert "Printer - Quantity: 0" in report
    assert "Monitor - Quantity: 0" in report
    out_of_stock_section = report.split("Out of Stock Products:", 1)[1]
    assert "Printer - Quantity: 0" in out_of_stock_section
    assert "Monitor - Quantity: 0" in out_of_stock_section
    assert "Laptop - Quantity: 5" not in out_of_stock_section
def test_generate_inventory_report_with_no_out_of_stock_products():
    inventory = InventoryService()
    inventory.add_product(Product(1, "Laptop", 850000, 5, "Electronics"))
    report = inventory.generate_inventory_report()
    assert "Out of Stock Products:" in report
    out_of_stock_section = report.split("Out of Stock Products:", 1)[1].split("Categories:", 1)[0]
    assert "Laptop - Quantity: 5" not in out_of_stock_section
def test_generate_inventory_report_out_of_stock_includes_category():
    inventory = InventoryService()
    inventory.add_product(Product(1, "Printer", 120000, 0, "Electronics"))
    report = inventory.generate_inventory_report()
    out_of_stock_section = report.split("Out of Stock Products:", 1)[1].split("Categories:", 1)[0]
    assert "Printer - Quantity: 0 - Category: Electronics" in out_of_stock_section
def test_generate_inventory_report_out_of_stock_includes_multiple_categories():
    inventory = InventoryService()
    inventory.add_product(Product(1, "Printer", 120000, 0, "Electronics"))
    inventory.add_product(Product(2, "Office Chair", 90000, 0, "Furniture"))
    report = inventory.generate_inventory_report()
    out_of_stock_section = report.split("Out of Stock Products:", 1)[1].split("Categories:", 1)[0]
    assert "Printer - Quantity: 0 - Category: Electronics" in out_of_stock_section
    assert "Office Chair - Quantity: 0 - Category: Furniture" in out_of_stock_section
def test_generate_inventory_report_uses_custom_low_stock_threshold():
    inventory = InventoryService()
    inventory.add_product(Product(1, "Laptop", 850000, 7, "Electronics"))
    inventory.add_product(Product(2, "Mouse", 15000, 12, "Electronics"))
    report = inventory.generate_inventory_report(low_stock_threshold=10)
    low_stock_section = report.split("Low Stock Products:", 1)[1].split("Out of Stock Products:", 1)[0]
    assert "Laptop - Quantity: 7" in low_stock_section
    assert "Mouse - Quantity: 12" not in low_stock_section
def test_generate_inventory_report_includes_product_at_low_stock_threshold():
    inventory = InventoryService()
    inventory.add_product(Product(1, "Keyboard", 25000, 10, "Electronics"))
    report = inventory.generate_inventory_report(low_stock_threshold=10)
    low_stock_section = report.split("Low Stock Products:", 1)[1].split("Out of Stock Products:", 1)[0]
    assert "Keyboard - Quantity: 10" in low_stock_section
def test_generate_inventory_report_rejects_negative_low_stock_threshold():
    inventory = InventoryService()
    with pytest.raises(ValueError, match="Low stock threshold cannot be negative"):
        inventory.generate_inventory_report(low_stock_threshold=-1)
def test_generate_inventory_report_rejects_non_integer_low_stock_threshold():
    inventory = InventoryService()
    with pytest.raises(ValueError, match="Low stock threshold must be an integer"):
        inventory.generate_inventory_report(low_stock_threshold=5.5)
def test_generate_inventory_report_rejects_boolean_low_stock_threshold():
    inventory = InventoryService()
    with pytest.raises(ValueError, match="Low stock threshold must be an integer"):
        inventory.generate_inventory_report(low_stock_threshold=True)
def test_generate_inventory_report_uses_custom_title():
    inventory = InventoryService()
    report = inventory.generate_inventory_report(title="MONTHLY INVENTORY REPORT")
    assert "MONTHLY INVENTORY REPORT" in report
    assert "INVENTORY REPORT" not in report.split("MONTHLY INVENTORY REPORT", 1)[0]
def test_generate_inventory_report_rejects_empty_title():
    inventory = InventoryService()
    with pytest.raises(ValueError, match="Report title cannot be empty"):
        inventory.generate_inventory_report(title="")
def test_generate_inventory_report_rejects_whitespace_title():
    inventory = InventoryService()
    with pytest.raises(ValueError, match="Report title cannot be empty"):
        inventory.generate_inventory_report(title="   ")
def test_generate_inventory_report_custom_title_is_heading():
    inventory = InventoryService()
    report = inventory.generate_inventory_report(title="MONTHLY INVENTORY REPORT")
    first_lines = report.splitlines()
    assert first_lines[1] == "           MONTHLY INVENTORY REPORT"
def test_generate_inventory_report_filters_by_category():
    inventory = InventoryService()
    inventory.add_product(Product(1, "Laptop", 850000, 5, "Electronics"))
    inventory.add_product(Product(2, "Office Chair", 120000, 3, "Furniture"))
    report = inventory.generate_inventory_report(category="Electronics")
    assert "Laptop" in report
    assert "Office Chair" not in report
def test_generate_inventory_report_category_filter_limits_category_section():
    inventory = InventoryService()
    inventory.add_product(Product(1, "Laptop", 850000, 5, "Electronics"))
    inventory.add_product(Product(2, "Office Chair", 120000, 3, "Furniture"))
    report = inventory.generate_inventory_report(category="Electronics")
    categories_section = report.split("Categories:", 1)[1]
    assert "Electronics" in categories_section
    assert "Furniture" not in categories_section
def test_generate_inventory_report_category_filter_limits_out_of_stock_section():
    inventory = InventoryService()
    inventory.add_product(Product(1, "Laptop", 850000, 0, "Electronics"))
    inventory.add_product(Product(2, "Office Chair", 120000, 0, "Furniture"))
    report = inventory.generate_inventory_report(category="Electronics")
    out_of_stock_section = report.split("Out of Stock Products:", 1)[1]
    assert "Laptop" in out_of_stock_section
    assert "Office Chair" not in out_of_stock_section
def test_generate_inventory_report_rejects_whitespace_category():
    inventory = InventoryService()
    with pytest.raises(ValueError, match="Category cannot be empty"):
        inventory.generate_inventory_report(category="   ")
def test_update_product_details():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 5, "Electronics")
    inventory.add_product(product)
    inventory.update_product(1, name="Laptop Pro", price=900000, category="Computers")
    updated_product = inventory.get_product(1)
    assert updated_product.name == "Laptop Pro"
    assert updated_product.price == 900000
    assert updated_product.category == "Computers"
    assert updated_product.product_id == 1
    assert updated_product.quantity == 5
def test_update_product_rejects_empty_name():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 5, "Electronics")
    inventory.add_product(product)
    with pytest.raises(ValueError, match="Product name cannot be empty"):
        inventory.update_product(1, name="   ")
def test_update_product_rejects_negative_price():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 5, "Electronics")
    inventory.add_product(product)
    with pytest.raises(ValueError, match="Price cannot be negative"):
        inventory.update_product(1, price=-100)
def test_update_product_rejects_empty_category():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 5, "Electronics")
    inventory.add_product(product)
    with pytest.raises(ValueError, match="Category cannot be empty"):
        inventory.update_product(1, category="   ")
def test_update_product_partial_update():
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 5, "Electronics")
    inventory.add_product(product)
    inventory.update_product(1, price=900000)
    updated_product = inventory.get_product(1)
    assert updated_product.name == "Laptop"
    assert updated_product.price == 900000
    assert updated_product.category == "Electronics"
    assert updated_product.product_id == 1
    assert updated_product.quantity == 5
def test_update_product_not_found():
    inventory = InventoryService()
    with pytest.raises(ValueError, match="Product not found"):
        inventory.update_product(999, price=500000)
def test_remove_product_moves_product_to_removed_products():
    from app.inventory_service import InventoryService
    from app.models import Product
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 5)
    inventory.add_product(product)
    inventory.remove_product(1)
    assert inventory.get_all_products() == []
    assert product in inventory.removed_products
def test_restore_product_moves_product_back_to_inventory():
    from app.inventory_service import InventoryService
    from app.models import Product
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 5)
    inventory.add_product(product)
    inventory.remove_product(1)
    inventory.restore_product(1)
    assert product in inventory.get_all_products()
    assert product not in inventory.removed_products
def test_restore_product_not_found():
    from app.inventory_service import InventoryService
    inventory = InventoryService()
    with pytest.raises(ValueError, match="Removed product not found"):
        inventory.restore_product(999)
def test_restore_product_rejects_duplicate_active_product_id():
    from app.inventory_service import InventoryService
    from app.models import Product
    inventory = InventoryService()
    removed_product = Product(1, "Laptop", 850000, 5)
    active_product = Product(1, "Mouse", 15000, 2)
    inventory.add_product(removed_product)
    inventory.remove_product(1)
    inventory.add_product(active_product)
    with pytest.raises(ValueError, match="Product ID already exists"):
        inventory.restore_product(1)
    assert active_product in inventory.get_all_products()
    assert removed_product in inventory.removed_products
def test_get_removed_products_returns_removed_products():
    from app.inventory_service import InventoryService
    from app.models import Product
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 5)
    inventory.add_product(product)
    inventory.remove_product(1)
    removed_products = inventory.get_removed_products()
    assert removed_products == [product]
def test_permanently_delete_removed_product():
    from app.inventory_service import InventoryService
    from app.models import Product
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 5)
    inventory.add_product(product)
    inventory.remove_product(1)
    inventory.permanently_delete_product(1)
    assert product not in inventory.removed_products
    assert inventory.get_all_products() == []
def test_permanently_delete_product_not_found():
    from app.inventory_service import InventoryService
    from app.models import Product
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 5)
    inventory.add_product(product)
    with pytest.raises(ValueError, match="Removed product not found"):
        inventory.permanently_delete_product(1)
    assert product in inventory.get_all_products()
def test_permanently_deleted_product_is_saved_in_deleted_history():
    from app.inventory_service import InventoryService
    from app.models import Product
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 5)
    inventory.add_product(product)
    inventory.remove_product(1)
    inventory.permanently_delete_product(1)
    assert product in inventory.deleted_products
def test_multiple_permanently_deleted_products_are_saved_in_deleted_history():
    from app.inventory_service import InventoryService
    from app.models import Product
    inventory = InventoryService()
    product1 = Product(1, "Laptop", 850000, 5)
    product2 = Product(2, "Mouse", 15000, 2)
    inventory.add_product(product1)
    inventory.add_product(product2)
    inventory.remove_product(1)
    inventory.remove_product(2)
    inventory.permanently_delete_product(1)
    inventory.permanently_delete_product(2)
    assert len(inventory.deleted_products) == 2
    assert inventory.deleted_products[0]["product"]["product_id"] == 1
    assert inventory.deleted_products[0]["product"]["name"] == "Laptop"
    assert inventory.deleted_products[0]["product"]["price"] == 850000
    assert inventory.deleted_products[0]["product"]["quantity"] == 5
    assert inventory.deleted_products[1]["product"]["product_id"] == 2
    assert inventory.deleted_products[1]["product"]["name"] == "Mouse"
    assert inventory.deleted_products[1]["product"]["price"] == 15000
    assert inventory.deleted_products[1]["product"]["quantity"] == 2
    assert inventory.deleted_products[0]["deleted_at"]
    assert inventory.deleted_products[1]["deleted_at"]
def test_get_deleted_products_returns_deleted_history():
    from app.inventory_service import InventoryService
    from app.models import Product
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 5)
    inventory.add_product(product)
    inventory.remove_product(1)
    inventory.permanently_delete_product(1)
    result = inventory.get_deleted_products()
    assert result == inventory.deleted_products
    assert result is not inventory.deleted_products
    assert result[0]["product"]["product_id"] == 1
    assert result[0]["product"]["name"] == "Laptop"
    assert result[0]["product"]["price"] == 850000
    assert result[0]["product"]["quantity"] == 5
    assert result[0]["product"]["category"] == "Uncategorized"
    assert result[0]["deleted_at"]
def test_permanently_deleted_product_is_saved_in_deleted_history():
    from app.inventory_service import InventoryService
    from app.models import Product
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 5)
    inventory.add_product(product)
    inventory.remove_product(1)
    inventory.permanently_delete_product(1)
    deleted_record = inventory.deleted_products[0]
    assert deleted_record["product"]["product_id"] == 1
    assert deleted_record["product"]["name"] == "Laptop"
    assert deleted_record["product"]["price"] == 850000
    assert deleted_record["product"]["quantity"] == 5
    assert deleted_record["product"]["category"] == "Uncategorized"
    assert deleted_record["deleted_at"]
def test_permanently_deleted_product_records_delete_action():
    from app.inventory_service import InventoryService
    from app.models import Product
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 5)
    inventory.add_product(product)
    inventory.remove_product(1)
    inventory.permanently_delete_product(1)
    deleted_record = inventory.deleted_products[0]
    assert deleted_record["product"]["product_id"] == 1
    assert deleted_record["product"]["name"] == "Laptop"
    assert deleted_record["product"]["price"] == 850000
    assert deleted_record["product"]["quantity"] == 5
    assert deleted_record["action"] == "PERMANENT_DELETE"
def test_permanently_deleted_product_records_product_snapshot():
    from app.inventory_service import InventoryService
    from app.models import Product
    inventory = InventoryService()
    product = Product(1, "Laptop", 850000, 5, "Electronics")
    inventory.add_product(product)
    inventory.remove_product(1)
    inventory.permanently_delete_product(1)
    deleted_record = inventory.deleted_products[0]
    snapshot = deleted_record["product"]
    assert snapshot["product_id"] == 1
    assert snapshot["name"] == "Laptop"
    assert snapshot["price"] == 850000
    assert snapshot["quantity"] == 5
    assert snapshot["category"] == "Electronics"
def test_permanently_deleted_product_records_unique_record_id():
    from app.inventory_service import InventoryService
    from app.models import Product
    inventory = InventoryService()
    product1 = Product(1, "Laptop", 850000, 5)
    product2 = Product(2, "Mouse", 15000, 2)
    inventory.add_product(product1)
    inventory.add_product(product2)
    inventory.remove_product(1)
    inventory.remove_product(2)
    inventory.permanently_delete_product(1)
    inventory.permanently_delete_product(2)
    first_record = inventory.deleted_products[0]
    second_record = inventory.deleted_products[1]
    assert first_record["record_id"] == 1
    assert second_record["record_id"] == 2
    assert first_record["record_id"] != second_record["record_id"]
def test_deleted_record_id_continues_after_multiple_deletions():
    from app.inventory_service import InventoryService
    from app.models import Product
    inventory = InventoryService()
    product1 = Product(1, "Laptop", 850000, 5)
    product2 = Product(2, "Mouse", 15000, 2)
    product3 = Product(3, "Keyboard", 25000, 3)
    inventory.add_product(product1)
    inventory.add_product(product2)
    inventory.add_product(product3)
    inventory.remove_product(1)
    inventory.remove_product(2)
    inventory.remove_product(3)
    inventory.permanently_delete_product(1)
    inventory.permanently_delete_product(2)
    inventory.permanently_delete_product(3)
    assert inventory.deleted_products[0]["record_id"] == 1
    assert inventory.deleted_products[1]["record_id"] == 2
    assert inventory.deleted_products[2]["record_id"] == 3