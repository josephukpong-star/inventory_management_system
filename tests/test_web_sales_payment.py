import json

import pytest

import web.app as web_app
from web.app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.test_client() as test_client:
        with test_client.session_transaction() as session:
            session["username"] = "test_admin"
            session["role"] = "Admin"

        yield test_client

def test_sale_saves_selected_payment_method(client, tmp_path, monkeypatch):
    inventory_file = tmp_path / "test_inventory.json"

    test_inventory = {"products": [{"product_id": 999, "name": "Payment Test Product", "category": "Testing", "price": 100, "selling_price": 150, "quantity": 10,}], "transactions": [],}

    inventory_file.write_text(json.dumps(test_inventory), encoding="utf-8",)

    monkeypatch.setattr(web_app, "DEFAULT_INVENTORY_FILE", str(inventory_file),)

    response = client.post("/sales", data={"product_id": "999", "quantity": "2", "price": "150", "payment_method": "Bank Transfer",}, follow_redirects=False,)

    assert response.status_code == 302

    saved_inventory = json.loads(inventory_file.read_text(encoding="utf-8"))

    assert saved_inventory["products"][0]["quantity"] == 8
    assert len(saved_inventory["transactions"]) == 1
    assert (saved_inventory["transactions"][0]["payment_method"] == "Bank Transfer")

def test_multiple_product_sale_saves_both_products_and_shared_reference(client, tmp_path, monkeypatch):
    inventory_file = tmp_path / "multi_sale_inventory.json"

    test_inventory = {
        "products": [{"product_id": 1001, "name": "Test Laptop", "category": "Electronics", "price": 500, "selling_price": 700, "quantity": 10,},{"product_id": 1002, "name": "Test Mouse", "category": "Accessories", "price": 100, "selling_price": 150, "quantity": 20,},], "transactions": [],}

    inventory_file.write_text(json.dumps(test_inventory), encoding="utf-8")
    monkeypatch.setattr(web_app, "DEFAULT_INVENTORY_FILE", str(inventory_file))

    response = client.post("/sales", data={"product_id": ["1001", "1002"], "quantity": ["2", "3"], "price": ["700", "150"], "payment_method": "Cash",}, follow_redirects=False,)

    assert response.status_code == 302

    saved_inventory = json.loads(inventory_file.read_text(encoding="utf-8"))

    products = {product["product_id"]: product for product in saved_inventory["products"]}
    transactions = saved_inventory["transactions"]

    assert products[1001]["quantity"] == 8
    assert products[1002]["quantity"] == 17
    assert len(transactions) == 2

    assert transactions[0]["payment_method"] == "Cash"
    assert transactions[1]["payment_method"] == "Cash"

    assert transactions[0]["sale_reference"]
    assert (transactions[0]["sale_reference"] == transactions[1]["sale_reference"])

    assert transactions[0]["sales_value"] == 1400
    assert transactions[1]["sales_value"] == 450


def test_duplicate_product_lines_are_rejected_without_changing_stock(client, tmp_path, monkeypatch):
    inventory_file = tmp_path / "duplicate_sale_inventory.json"
    test_inventory = {"products": [{"product_id": 1003, "name": "Test Keyboard", "category": "Accessories", "price": 200, "selling_price": 300, "quantity": 10,}], "transactions": [],}
    inventory_file.write_text(json.dumps(test_inventory), encoding="utf-8")
    monkeypatch.setattr(web_app, "DEFAULT_INVENTORY_FILE", str(inventory_file))

    response = client.post("/sales", data={"product_id": ["1003", "1003"], "quantity": ["2", "3"], "price": ["300", "300"], "payment_method": "Cash",}, follow_redirects=False,)
    assert response.status_code == 302

    saved_inventory = json.loads(inventory_file.read_text(encoding="utf-8"))
    assert saved_inventory["products"][0]["quantity"] == 10
    assert saved_inventory["transactions"] == []


def test_insufficient_stock_rejects_entire_multi_product_sale(client, tmp_path, monkeypatch):
    inventory_file = tmp_path / "insufficient_stock_inventory.json"

    test_inventory = {"products": [{"product_id": 1004, "name": "Test Monitor", "category": "Electronics", "price": 500, "selling_price": 700, "quantity": 10,},{"product_id": 1005, "name": "Test Webcam", "category": "Electronics", "price": 200, "selling_price": 350, "quantity": 2,},], "transactions": [],}
    inventory_file.write_text(json.dumps(test_inventory), encoding="utf-8")
    monkeypatch.setattr(web_app, "DEFAULT_INVENTORY_FILE", str(inventory_file))
    response = client.post("/sales", data={"product_id": ["1004", "1005"], "quantity": ["3", "5"], "price": ["700", "350"], "payment_method": "Bank Transfer",}, follow_redirects=False,)

    assert response.status_code == 302
    saved_inventory = json.loads(inventory_file.read_text(encoding="utf-8"))
    products = {product["product_id"]: product for product in saved_inventory["products"]}

    assert products[1004]["quantity"] == 10
    assert products[1005]["quantity"] == 2
    assert saved_inventory["transactions"] == []

def test_multi_product_sale_save_failure_preserves_inventory_file(client, tmp_path, monkeypatch):
    import json
    import web.app as web_app

    inventory_file = tmp_path / "test_inventory.json"

    original_inventory = {"products": [{"product_id": 901, "name": "Test Laptop", "category": "Electronics", "price": 100, "selling_price": 150, "quantity": 10,},{"product_id": 902, "name": "Test Mouse", "category": "Accessories", "price": 20, "selling_price": 35, "quantity": 20,},], "transactions": [],}

    original_content = json.dumps(original_inventory, indent=4)
    inventory_file.write_text(original_content, encoding="utf-8")

    monkeypatch.setattr(web_app, "DEFAULT_INVENTORY_FILE", str(inventory_file))

    def fail_save(self, file_path): 
        raise OSError("Simulated inventory save failure") 
    monkeypatch.setattr( web_app.InventoryService, "save_inventory", fail_save ) 
    response = client.post( "/sales", data={ "product_id": ["901", "902"], "quantity": ["2", "3"], "price": ["150", "35"], "payment_method": "Cash", }, follow_redirects=False, ) 
    assert response.status_code == 302 
    saved_content = inventory_file.read_text(encoding="utf-8") 
    assert saved_content == original_content