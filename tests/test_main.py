from unittest.mock import patch
def test_main_exits():
    from app.main import main
    with patch("app.ui.display_menu"), \
         patch("app.ui.get_menu_choice", return_value=15), \
         patch("builtins.print") as mock_print:
        main()
        mock_print.assert_any_call("Goodbye!")
def test_main_transaction_history():
    from app.main import main
    with patch("app.ui.display_menu"), \
         patch("app.ui.get_menu_choice", side_effect=[12, 15]), \
         patch("app.ui.display_transaction_history") as mock_display_history, \
         patch("builtins.print"):
        inventory = main()
        mock_display_history.assert_called_once_with([])
def test_main_transaction_history_with_transaction():
    from app.main import main
    from app.models import Product
    product = Product(1, "Laptop", 850000, 10)
    with patch("app.ui.display_menu"), \
         patch("app.ui.get_menu_choice", side_effect=[1, 4, 12, 15]), \
         patch("app.ui.get_product_input", return_value=product), \
         patch("app.ui.get_product_id", return_value=1), \
         patch("app.ui.get_quantity_change", return_value=5), \
         patch("app.ui.display_transaction_history") as mock_display_history, \
         patch("builtins.print"):
        inventory = main()
        mock_display_history.assert_called_once()
        transactions = mock_display_history.call_args[0][0]
        assert len(transactions) == 1
        assert transactions[0]["product_id"] == 1
        assert transactions[0]["product_name"] == "Laptop"
        assert transactions[0]["type"] == "STOCK-IN"
        assert transactions[0]["quantity"] == 5
        assert transactions[0]["price"] == 850000
        assert transactions[0]["total_value"] == 4250000
def test_main_add_product():
    from app.main import main
    from app.models import Product
    product = Product(1, "Laptop", 850000, 5)
    with patch("app.ui.display_menu"), \
         patch("app.ui.get_menu_choice", side_effect=[1, 15]), \
         patch("app.ui.get_product_input", return_value=product), \
         patch("builtins.print"):
        inventory = main()
        assert inventory.get_product(1) == product
def test_main_view_products():
    from app.main import main
    from app.models import Product
    product = Product(1, "Laptop", 850000, 5)
    with patch("app.ui.display_menu"), \
         patch("app.ui.get_menu_choice", side_effect=[1, 2, 15]), \
         patch("app.ui.get_product_input", return_value=product), \
         patch("app.ui.display_products") as mock_display_products, \
         patch("builtins.print"):
        main()
        mock_display_products.assert_called_once()
        displayed_products = mock_display_products.call_args[0][0]
        assert product in displayed_products
def test_main_search_product():
    from app.main import main
    from app.models import Product
    product = Product(1, "Laptop", 850000, 5)
    with patch("app.ui.display_menu"), \
         patch("app.ui.get_menu_choice", side_effect=[1, 3, 15]), \
         patch("app.ui.get_product_input", return_value=product), \
         patch("app.ui.get_search_term", return_value="laptop"), \
         patch("app.ui.display_products") as mock_display_products, \
         patch("builtins.print"):
        main()
        mock_display_products.assert_called_once()
        displayed_products = mock_display_products.call_args[0][0]
        assert product in displayed_products
def test_main_stock_in():
    from app.main import main
    from app.models import Product
    product = Product(1, "Laptop", 850000, 5)
    with patch("app.ui.display_menu"), \
         patch("app.ui.get_menu_choice", side_effect=[1, 4, 15]), \
         patch("app.ui.get_product_input", return_value=product), \
         patch("app.ui.get_product_id", return_value=1), \
         patch("app.ui.get_quantity_change", return_value=3), \
         patch("builtins.print"):
        inventory = main()
        updated_product = inventory.get_product(1)
        assert updated_product.quantity == 8
def test_main_stock_out():
    from app.main import main
    from app.models import Product
    product = Product(1, "Laptop", 850000, 10)
    with patch("app.ui.display_menu"), \
         patch("app.ui.get_menu_choice", side_effect=[1, 5, 15]), \
         patch("app.ui.get_product_input", return_value=product), \
         patch("app.ui.get_product_id", return_value=1), \
         patch("app.ui.get_quantity_change", return_value=3), \
         patch("builtins.print"):
        inventory = main()
        updated_product = inventory.get_product(1)
        assert updated_product.quantity == 7
def test_main_remove_product():
    from app.main import main
    from app.models import Product
    product = Product(1, "Laptop", 850000, 5)
    with patch("app.ui.display_menu"), \
         patch("app.ui.get_menu_choice", side_effect=[1, 6, 2, 15]), \
         patch("app.ui.get_product_input", return_value=product), \
         patch("app.ui.get_product_id", return_value=1), \
         patch("app.ui.display_products") as mock_display_products, \
         patch("builtins.print"):
        inventory = main()
        assert inventory.get_all_products() == []
        mock_display_products.assert_called_once()
        displayed_products = mock_display_products.call_args[0][0]
        assert displayed_products == []
def test_main_inventory_summary():
    from app.main import main
    from app.models import Product
    product1 = Product(1, "Laptop", 850000, 5)
    product2 = Product(2, "Mouse", 15000, 2)
    with patch("app.ui.display_menu"), \
         patch("app.ui.get_menu_choice", side_effect=[1, 1, 7, 15]), \
         patch("app.ui.get_product_input", side_effect=[product1, product2]), \
         patch("app.ui.display_inventory_summary") as mock_display_summary, \
         patch("builtins.print"):
        inventory = main()
        mock_display_summary.assert_called_once()
        summary = mock_display_summary.call_args[0][0]
        assert summary["total_products"] == 2
        assert summary["total_quantity"] == 7
        assert summary["total_value"] == 4_280_000
        assert summary["low_stock_count"] == 2
def test_main_save_inventory(tmp_path):
    from app.main import main
    from app.models import Product
    product = Product(1, "Laptop", 850000, 5)
    with patch("app.ui.display_menu"), \
         patch("app.ui.get_menu_choice", side_effect=[1, 8, 15]), \
         patch("app.ui.get_product_input", return_value=product), \
         patch("app.ui.get_product_id"), \
         patch("builtins.print"), \
         patch("app.inventory_service.save_inventory_data") as mock_save:
        inventory = main()
        mock_save.assert_called_once()
        saved_products = mock_save.call_args[0][0]
        saved_transactions = mock_save.call_args[0][1]
        assert saved_products == [product]
        assert saved_transactions == []
def test_main_load_inventory(tmp_path):
    from app.main import main
    from app.models import Product
    from app.storage import save_products
    file_path = tmp_path / "inventory.json"
    product1 = Product(1, "Laptop", 850000, 5)
    product2 = Product(2, "Mouse", 15000, 2)
    save_products([product1, product2], file_path)
    with patch("app.ui.display_menu"), \
         patch("app.ui.get_menu_choice", side_effect=[9, 2, 15]), \
         patch("app.ui.display_products") as mock_display_products, \
         patch("builtins.print"):
        inventory = main(file_path)
        mock_display_products.assert_called_once()
        displayed_products = mock_display_products.call_args[0][0]
        assert len(displayed_products) == 2
        assert displayed_products[0].name == "Laptop"
        assert displayed_products[1].name == "Mouse"
def test_main_load_inventory_with_transactions(tmp_path):
    from app.main import main
    from app.models import Product
    from app.storage import save_inventory_data
    file_path = tmp_path / "inventory.json"
    products = [Product(1, "Laptop", 850000, 15, "Electronics")]
    transactions = [{"product_id": 1, "product_name": "Laptop", "price": 850000, "type": "STOCK-IN", "quantity": 5, "total_value": 4250000, "timestamp": "2026-09-08T23:07:51"}]
    save_inventory_data(products, transactions, file_path)
    with patch("app.ui.display_menu"), \
         patch("app.ui.get_menu_choice", side_effect=[9, 12, 15]), \
         patch("app.ui.display_transaction_history") as mock_display_history, \
         patch("builtins.print"):
        inventory = main(file_path)
        mock_display_history.assert_called_once()
        loaded_transactions = mock_display_history.call_args[0][0]
        assert len(loaded_transactions) == 1
        assert loaded_transactions[0]["product_id"] == 1
        assert loaded_transactions[0]["product_name"] == "Laptop"
        assert loaded_transactions[0]["type"] == "STOCK-IN"
        assert loaded_transactions[0]["quantity"] == 5
        assert loaded_transactions[0]["total_value"] == 4250000
        loaded_products = inventory.get_all_products()
        assert len(loaded_products) == 1
        assert loaded_products[0].name == "Laptop"
        assert loaded_products[0].quantity == 15
def test_main_category_summary():
    from app.main import main
    with patch("app.ui.display_menu"), \
         patch("app.ui.get_menu_choice", side_effect=[10, 15]), \
         patch("app.ui.display_category_summary") as mock_display_summary, \
         patch("builtins.print"):
        inventory = main()
        mock_display_summary.assert_called_once_with({})
def test_main_inventory_report():
    from app.main import main
    with patch("app.ui.display_menu"), \
         patch("app.ui.get_menu_choice", side_effect=[11, 15]), \
         patch("app.ui.display_inventory_report") as mock_display_report, \
         patch("builtins.print"):
        inventory = main()
        mock_display_report.assert_called_once()
def test_main_save_inventory_report(monkeypatch):
    from app.main import main
    from unittest.mock import patch
    with patch("app.inventory_service.InventoryService.save_inventory_report") as mock_save_report: 
        choices = iter(["18", "15"])
        monkeypatch.setattr("builtins.input", lambda _: next(choices))
        main()
        mock_save_report.assert_called_once_with( "inventory_report.txt")
def test_main_dashboard(capsys):
    from unittest.mock import patch
    from app.main import main
    with patch("app.main.ui.get_menu_choice", side_effect=[16, 15]):
        main()
    captured = capsys.readouterr()
    assert "INVENTORY DASHBOARD" in captured.out
def test_main_inventory_alerts(monkeypatch, capsys):
    from app.main import main
    choices = iter(["17", "15",])
    monkeypatch.setattr("builtins.input", lambda _: next(choices))
    main()
    captured = capsys.readouterr()
    assert "INVENTORY ALERTS" in captured.out
def test_main_transaction_summary(monkeypatch, capsys):
    from app.main import main
    choices = iter(["13", "15"])
    monkeypatch.setattr("builtins.input", lambda _: next(choices))
    main()
    captured = capsys.readouterr()
    assert "TRANSACTION SUMMARY" in captured.out
def test_main_transaction_value_summary(monkeypatch, capsys):
    from app.main import main
    choices = iter(["14", "15"])
    monkeypatch.setattr("builtins.input", lambda _: next(choices))
    main()
    captured = capsys.readouterr()
    assert "TRANSACTION VALUE SUMMARY" in captured.out