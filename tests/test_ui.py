import pytest
from unittest.mock import patch
def test_display_menu(capsys):
    from app.ui import display_menu
    display_menu()
    captured = capsys.readouterr()
    assert "INVENTORY MANAGEMENT SYSTEM" in captured.out
    assert "1. Add Product" in captured.out
    assert "2. View Products" in captured.out
    assert "10. Category Summary" in captured.out
    assert "11. Inventory Report" in captured.out
    assert "12. Transaction History" in captured.out
    assert "13. Transaction Summary" in captured.out
    assert "14. Transaction Value Summary" in captured.out
    assert "15. Exit" in captured.out  
    assert "16. Dashboard" in captured.out
    assert "17. Inventory Alerts" in captured.out
def test_get_menu_choice_valid(monkeypatch):
    from app.ui import get_menu_choice
    monkeypatch.setattr("builtins.input", lambda _: "3")
    result = get_menu_choice()
    assert result == 3
def test_get_menu_choice_invalid_then_valid(monkeypatch):
    from app.ui import get_menu_choice
    inputs = iter(["abc", "20", "19"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    result = get_menu_choice()
    assert result == 19
def test_display_products(capsys):
    from app.ui import display_products
    from app.models import Product
    products = [Product(1, "Laptop", 850000, 5), Product(2, "Mouse", 15000, 10),]
    display_products(products)
    captured = capsys.readouterr()
    assert "Laptop" in captured.out
    assert "850,000.00" in captured.out
    assert "Mouse" in captured.out
    assert "15,000.00" in captured.out
def test_display_products_empty(capsys):
    from app.ui import display_products
    display_products([])
    captured = capsys.readouterr()
    assert "No products found" in captured.out
def test_get_product_input(monkeypatch):
    from app.ui import get_product_input
    inputs = iter(["1", "Laptop", "850000", "5", "Electronics"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    product = get_product_input()
    assert product.product_id == 1
    assert product.name == "Laptop"
    assert product.price == 850000
    assert product.quantity == 5
def test_get_product_input_invalid_then_valid(monkeypatch):
    from app.ui import get_product_input
    inputs = iter(["abc", "1", "Laptop", "850000", "5", "Electronics"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    product = get_product_input()
    assert product.product_id == 1
    assert product.name == "Laptop"
    assert product.price == 850000
    assert product.quantity == 5
def test_get_product_input_negative_price_then_valid(monkeypatch):
    from app.ui import get_product_input
    inputs = iter(["1", "Laptop", "-500", "850000", "5", "Electronics"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    product = get_product_input()
    assert product.price == 850000
def test_get_product_input_negative_quantity_then_valid(monkeypatch):
    from app.ui import get_product_input
    inputs = iter(["1", "Laptop", "850000", "-5", "10", "Electronics"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    product = get_product_input()
    assert product.quantity == 10
def test_get_search_term(monkeypatch):
    from app.ui import get_search_term
    monkeypatch.setattr("builtins.input", lambda _: "laptop")
    result = get_search_term()
    assert result == "laptop"
def test_get_product_id(monkeypatch):
    from app.ui import get_product_id
    monkeypatch.setattr("builtins.input", lambda _: "1")
    result = get_product_id()
    assert result == 1
def test_get_quantity_change(monkeypatch):
    from app.ui import get_quantity_change
    monkeypatch.setattr("builtins.input", lambda _: "-3")
    result = get_quantity_change()
    assert result == -3
def test_display_inventory_summary(capsys):
    from app.ui import display_inventory_summary
    summary = {"total_products": 3, "total_quantity": 15, "total_value": 2450000, "low_stock_count": 1 }
    display_inventory_summary(summary)
    captured = capsys.readouterr()
    assert "INVENTORY SUMMARY" in captured.out
    assert "Total Products: 3" in captured.out
    assert "Total Quantity: 15" in captured.out
    assert "Total Inventory Value: ₦2,450,000.00" in captured.out
    assert "Low Stock: 1" in captured.out
def test_display_inventory_summary_includes_out_of_stock_count(capsys):
    from app.ui import display_inventory_summary
    summary = {"total_products": 4, "total_quantity": 18, "total_value": 740000, "low_stock_count": 1, "out_of_stock_count": 2}
    display_inventory_summary(summary)
    captured = capsys.readouterr()
    assert "Out of Stock: 2" in captured.out    
def test_format_currency():
    from app.ui import format_currency
    assert format_currency(850000) == "₦850,000.00"
    assert format_currency(15000) == "₦15,000.00"
    assert format_currency(4530000.0) == "₦4,530,000.00"
def test_display_products_includes_stock_status(capsys):
    from app.models import Product
    from app.ui import display_products
    product = Product(1, "Laptop", 500000, 3)
    display_products([product])
    captured = capsys.readouterr()
    assert "Stock Status: LOW STOCK" in captured.out
def test_display_products_shows_in_stock_status(capsys):
    from app.models import Product
    from app.ui import display_products
    product = Product(1, "Laptop", 500000, 10)
    display_products([product])
    captured = capsys.readouterr()
    assert "Stock Status: IN STOCK" in captured.out
def test_display_products_shows_out_of_stock_status(capsys):
    from app.models import Product
    from app.ui import display_products
    product = Product(1, "Keyboard", 25000, 0)
    display_products([product])
    captured = capsys.readouterr()
    assert "Stock Status: OUT OF STOCK" in captured.out
def test_get_stock_status():
    from app.ui import get_stock_status
    assert get_stock_status(0) == "OUT OF STOCK"
    assert get_stock_status(3) == "LOW STOCK"
    assert get_stock_status(10) == "IN STOCK"
def test_get_stock_status_with_custom_threshold():
    from app.ui import get_stock_status
    assert get_stock_status(8, low_stock_threshold=10) == "LOW STOCK"
    assert get_stock_status(11, low_stock_threshold=10) == "IN STOCK"
def test_get_stock_status_rejects_negative_threshold():
    from app.ui import get_stock_status
    with pytest.raises(ValueError, match="Low stock threshold cannot be negative"):
        get_stock_status(5, low_stock_threshold=-1)
def test_get_stock_status_rejects_non_integer_threshold():
    from app.ui import get_stock_status
    with pytest.raises(ValueError, match="Low stock threshold must be an integer"):
        get_stock_status(5, low_stock_threshold=5.5)
def test_get_stock_status_rejects_boolean_threshold():
    from app.ui import get_stock_status
    with pytest.raises(ValueError, match="Low stock threshold must be an integer"):
        get_stock_status(5, low_stock_threshold=True)
def test_get_product_input_with_category():
    from app.ui import get_product_input
    with patch("builtins.input", side_effect=["1", "Laptop", "850000", "10", "Electronics"]):
        product = get_product_input()
    assert product.product_id == 1
    assert product.name == "Laptop"
    assert product.price == 850000
    assert product.quantity == 10
    assert product.category == "Electronics"
def test_display_category_summary(capsys):
    from app.ui import display_category_summary
    summary = {"Electronics": {"product_count": 2, "total_quantity": 15, "total_value": 12750000}, "Furniture": {"product_count": 1, "total_quantity": 5, "total_value": 2500000}}
    display_category_summary(summary)
    captured = capsys.readouterr()
    assert "CATEGORY SUMMARY" in captured.out
    assert "Electronics" in captured.out
    assert "Products: 2" in captured.out
    assert "Quantity: 15" in captured.out
    assert "Value: ₦12,750,000.00" in captured.out
    assert "Furniture" in captured.out
    assert "Products: 1" in captured.out
    assert "Quantity: 5" in captured.out
    assert "Value: ₦2,500,000.00" in captured.out
def test_display_category_summary_empty(capsys):
    from app.ui import display_category_summary
    display_category_summary({})
    captured = capsys.readouterr()
    assert "CATEGORY SUMMARY" in captured.out
    assert "No categories found." in captured.out
def test_get_menu_choice_accepts_13(monkeypatch):
    from app.ui import get_menu_choice
    inputs = iter(["13"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    result = get_menu_choice()
    assert result == 13
def test_display_dashboard(capsys):
    from app.ui import display_dashboard
    dashboard_data = {"total_products": 3, "total_quantity": 13, "total_value": 8600000, "in_stock": 1, "low_stock": 1, "out_of_stock": 1, "stock_health": 66.66666666666666, "top_product": "Laptop",}
    display_dashboard(dashboard_data)
    captured = capsys.readouterr()
    assert "INVENTORY DASHBOARD" in captured.out
    assert "Total Products:" in captured.out
    assert "Total Quantity:" in captured.out
    assert "13" in captured.out
    assert "Inventory Value:" in captured.out
    assert "₦8,600,000.00" in captured.out
    assert "In Stock:" in captured.out
    assert "Low Stock:" in captured.out
    assert "Out of Stock:" in captured.out
    assert "Stock Health:" in captured.out
    assert "66.67%" in captured.out
    assert "Top Product:" in captured.out
    assert "Laptop" in captured.out
def test_display_dashboard_category_values(capsys):
    from app.ui import display_dashboard
    dashboard_data = {"total_products": 3, "total_quantity": 13, "total_value": 8600000, "in_stock": 1, "low_stock": 1, "out_of_stock": 1, "stock_health": 66.67, "top_product": "Laptop", "category_values": {"Electronics": 8600000, "Furniture": 0,}, "top_category": "Electronics",}
    display_dashboard(dashboard_data)
    captured = capsys.readouterr()
    assert "Categories:" in captured.out
    assert "Electronics" in captured.out
    assert "₦8,600,000.00" in captured.out
    assert "Furniture" in captured.out
    assert "Top Category:" in captured.out
    assert "Electronics" in captured.out
def test_display_dashboard_attention_products(capsys):
    from app.ui import display_dashboard
    dashboard_data = {"total_products": 3, "total_quantity": 13, "total_value": 8600000, "in_stock": 1, "low_stock": 1, "out_of_stock": 1, "stock_health": 66.66666666666666, "top_product": "Laptop", "top_category": "Electronics", "category_values": {"Electronics": 8600000, "Furniture": 0,}, "attention_products": ["Phone", "Chair"],}
    display_dashboard(dashboard_data)
    captured = capsys.readouterr()
    assert "Attention Required:" in captured.out
    assert "- Phone" in captured.out
    assert "- Chair" in captured.out
def test_display_dashboard_no_attention_products(capsys):
    from app.ui import display_dashboard
    dashboard_data = {"total_products": 0, "total_quantity": 0, "total_value": 0, "in_stock": 0, "low_stock": 0, "out_of_stock": 0, "stock_health": 0.0, "top_product": None, "top_category": None, "category_values": {}, "attention_products": [],}
    display_dashboard(dashboard_data)
    captured = capsys.readouterr()
    assert "Attention Required:" in captured.out
    assert "None" in captured.out
def test_display_dashboard_inventory_value_percentage(capsys):
    from app.ui import display_dashboard
    dashboard_data = {"total_products": 2, "total_quantity": 13, "total_value": 8600000, "in_stock": 1, "low_stock": 1, "out_of_stock": 0, "stock_health": 100.0, "top_product": "Laptop", "top_category": "Electronics", "category_values": {"Electronics": 8600000,}, "inventory_value_percentage": {"Laptop": 93.02, "Phone": 6.98,}, "attention_products": ["Phone"],}
    display_dashboard(dashboard_data)
    captured = capsys.readouterr()
    assert "Inventory Value Distribution:" in captured.out
    assert "Laptop: 93.02%" in captured.out
    assert "Phone: 6.98%" in captured.out
def test_display_dashboard_top_products_by_inventory_value(capsys):
    from app.ui import display_dashboard
    dashboard_data = {"total_products": 3, "total_quantity": 18, "total_value": 8500000, "in_stock": 3, "low_stock": 0, "out_of_stock": 0, "stock_health": 100.0, "top_product": "Laptop", "top_category": "Electronics", "category_values": {"Electronics": 8600000,}, "inventory_value_percentage": {"Laptop": 94.12, "Phone": 7.06, "Chair": 0.0,}, "top_products_by_value": [ "Laptop", "Phone", "Chair",], "attention_products": [],}
    display_dashboard(dashboard_data)
    captured = capsys.readouterr()
    assert "Top Products by Inventory Value:" in captured.out
    assert "1. Laptop" in captured.out
    assert "2. Phone" in captured.out
    assert "3. Chair" in captured.out
def test_display_dashboard_no_top_products(capsys):
    from app.ui import display_dashboard
    dashboard_data = {"total_products": 0, "total_quantity": 0, "total_value": 0, "in_stock": 0, "low_stock": 0, "out_of_stock": 0, "stock_health": 0.0, "top_product": None, "top_category": None, "category_values": {}, "inventory_value_percentage": {}, "top_products_by_value": [], "attention_products": [],}
    display_dashboard(dashboard_data)
    captured = capsys.readouterr()
    assert "Top Products by Inventory Value:" in captured.out
def test_display_dashboard_top_products_with_values(capsys):
    from app.ui import display_dashboard
    dashboard_data = {"total_products": 3, "total_quantity": 18, "total_value": 9100000, "in_stock": 3, "low_stock": 0, "out_of_stock": 0, "stock_health": 100.0, "top_product": "Laptop", "top_category": "Electronics", "category_values": {"Electronics": 8600000, "Furniture": 500000,}, "inventory_value_percentage": {"Laptop": 87.91, "Phone": 6.59, "Chair": 5.49,}, "top_products_by_value": ["Laptop", "Phone", "Chair",], "top_products_with_values": [{"name": "Laptop", "value": 8000000}, {"name": "Phone", "value": 600000}, {"name": "Chair", "value": 500000},], "attention_products": [],}
    display_dashboard(dashboard_data)
    captured = capsys.readouterr()
    assert "Top Products by Inventory Value:" in captured.out
    assert "1. Laptop - ₦8,000,000.00" in captured.out
    assert "2. Phone - ₦600,000.00" in captured.out
    assert "3. Chair - ₦500,000.00" in captured.out
def test_display_dashboard_attention_count(capsys):
    from app.ui import display_dashboard
    dashboard_data = {"total_products": 3, "total_quantity": 13, "total_value": 180000, "in_stock": 1, "low_stock": 1, "out_of_stock": 1, "stock_health": 66.67, "top_product": "Laptop", "top_category": "Electronics", "attention_count": 2, "attention_products": ["Laptop", "Phone"], "top_products_with_values": [], "inventory_value_percentage": {}, "category_values": {},}
    display_dashboard(dashboard_data)
    captured = capsys.readouterr()
    assert "Attention Required: 2" in captured.out
def test_display_inventory_alerts(capsys):
    from app.ui import display_inventory_alerts
    alerts = [{"product_id": 1, "product_name": "Laptop", "status": "LOW STOCK", "quantity": 3,}, {"product_id": 2, "product_name": "Phone", "status": "OUT OF STOCK", "quantity": 0, },]
    display_inventory_alerts(alerts)
    captured = capsys.readouterr()
    assert "INVENTORY ALERTS" in captured.out
    assert "Laptop" in captured.out
    assert "LOW STOCK" in captured.out
    assert "3 units" in captured.out
    assert "Phone" in captured.out
    assert "OUT OF STOCK" in captured.out
    assert "0 units" in captured.out
def test_display_inventory_alerts_empty(capsys):
    from app.ui import display_inventory_alerts
    display_inventory_alerts([])
    captured = capsys.readouterr()
    assert "INVENTORY ALERTS" in captured.out
    assert "No inventory alerts." in captured.out
def test_display_transaction_summary(capsys):
    from app.ui import display_transaction_summary
    summary = {"total_transactions": 8, "stock_in_transactions": 5, "stock_out_transactions": 3, "total_stock_in_quantity": 45, "total_stock_out_quantity": 18,}
    display_transaction_summary(summary)
    captured = capsys.readouterr()
    assert "TRANSACTION SUMMARY" in captured.out
    assert "Total Transactions: 8" in captured.out
    assert "Stock-In Transactions: 5" in captured.out
    assert "Stock-Out Transactions: 3" in captured.out
    assert "Total Stock-In Quantity: 45" in captured.out
    assert "Total Stock-Out Quantity: 18" in captured.out
def test_display_transaction_summary_empty(capsys):
    from app.ui import display_transaction_summary
    summary = {"total_transactions": 0, "stock_in_transactions": 0, "stock_out_transactions": 0, "total_stock_in_quantity": 0, "total_stock_out_quantity": 0,}
    display_transaction_summary(summary)
    captured = capsys.readouterr()
    assert "TRANSACTION SUMMARY" in captured.out
    assert "Total Transactions: 0" in captured.out
    assert "Stock-In Transactions: 0" in captured.out
    assert "Stock-Out Transactions: 0" in captured.out
    assert "Total Stock-In Quantity: 0" in captured.out
    assert "Total Stock-Out Quantity: 0" in captured.out
def test_display_transaction_value_summary(capsys):
    from app.ui import display_transaction_value_summary
    summary = {"total_stock_in_value": 1000000, "total_stock_out_value": 400000,}
    display_transaction_value_summary(summary)
    captured = capsys.readouterr()
    assert "TRANSACTION VALUE SUMMARY" in captured.out
    assert "Total Stock-In Value: ₦1,000,000.00" in captured.out
    assert "Total Stock-Out Value: ₦400,000.00" in captured.out
def test_display_transaction_value_summary_empty(capsys):
    from app.ui import display_transaction_value_summary
    summary = {"total_stock_in_value": 0, "total_stock_out_value": 0,}
    display_transaction_value_summary(summary)
    captured = capsys.readouterr()
    assert "TRANSACTION VALUE SUMMARY" in captured.out
    assert "Total Stock-In Value: ₦0.00" in captured.out
    assert "Total Stock-Out Value: ₦0.00" in captured.out
def test_display_menu_includes_save_inventory_report(capsys):
    from app.ui import display_menu
    display_menu()
    captured = capsys.readouterr()
    assert "18. Save Inventory Report" in captured.out
def test_get_product_update_input(monkeypatch):
    from app.ui import get_product_update_input
    inputs = iter(["1", "Laptop Pro", "900000", "Computers",])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    result = get_product_update_input()
    assert result == (1, "Laptop Pro", 900000.0, "Computers")
def test_get_product_update_input_partial_update(monkeypatch):
    from app.ui import get_product_update_input
    inputs = iter(["1", "", "950000", "",])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    result = get_product_update_input()
    assert result == (1, None, 950000.0, None)
def test_get_confirmation_yes(monkeypatch):
    from app.ui import get_confirmation
    monkeypatch.setattr("builtins.input", lambda _: "y")
    result = get_confirmation("Are you sure you want to remove this product?")
    assert result is True
def test_get_confirmation_no(monkeypatch):
    from app.ui import get_confirmation
    monkeypatch.setattr("builtins.input", lambda _: "n")
    result = get_confirmation("Are you sure you want to remove this product?")
    assert result is False
def test_get_confirmation_invalid_then_valid(monkeypatch, capsys):
    from app.ui import get_confirmation
    inputs = iter(["maybe", "y"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    result = get_confirmation("Are you sure you want to remove this product?")
    assert result is True
    captured = capsys.readouterr()
    assert "Invalid input. Please enter y or n." in captured.out