import json

import pytest

from web.app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.test_client() as test_client:
        yield test_client

@pytest.fixture
def authenticated_client(client, tmp_path, monkeypatch):
    import web.app as web_app
    inventory_file = tmp_path / "inventory.json"
    monkeypatch.setattr(web_app, "INVENTORY_FILE", str(inventory_file))

    with client.session_transaction() as session:
        session["username"] = "test_admin"
        session["role"] = "Admin"
    return client, inventory_file

def test_add_product_page_displays_basic_product_fields(authenticated_client):
    client, _ = authenticated_client

    response = client.get("/products/add")

    assert response.status_code == 200

    page = response.get_data(as_text=True)

    # Basic product fields must remain available.
    assert "Product ID" in page
    assert "Product Name" in page
    assert "Category" in page
    assert "Base Unit" in page
    assert "Cost Price per Base Unit" in page
    assert "Selling Price per Base Unit" in page
    assert "Opening Quantity" not in page

    # The single purchase unit and selling unit fields must be available.
    assert 'name="purchase_unit_name"' in page
    assert 'name="purchase_unit_factor"' in page
    assert 'name="selling_unit_name"' in page
    assert 'name="selling_unit_factor"' in page

    # The three-selling-unit configuration must not return.
    assert "Selling Unit 1" not in page
    assert "Selling Unit 2" not in page
    assert "Selling Unit 3" not in page

    # The form actions must remain available.
    assert "Save Product" in page
    assert "Cancel" in page

def test_add_product_saves_single_purchase_and_selling_unit(authenticated_client):
    client, inventory_file = authenticated_client

    response = client.post("/products/add", data={"product_id": "101", "name": "Eggs", "category": "Food", "price": "100", "selling_price": "150", "quantity": "300", "base_unit": "piece", "purchase_unit_name": "crate", "purchase_unit_factor": "30", "selling_unit_name": "half crate", "selling_unit_factor": "15",}, follow_redirects=False,)
    page = response.get_data(as_text=True)

    if "form-error" in page:
        start = page.find("form-error")
        print("\nVALIDATION MESSAGE:\n", page[start:start + 500])

    assert response.status_code == 302
    assert inventory_file.exists()

    saved_data = json.loads(inventory_file.read_text(encoding="utf-8"))
    saved_product = saved_data["products"][0]

    assert saved_product["product_id"] == 101
    assert saved_product["name"] == "Eggs"
    assert saved_product["price"] == 100
    assert saved_product["selling_price"] == 150
    assert saved_product["quantity"] == 0
    assert saved_product["base_unit"] == "piece"

    assert saved_product["purchase_units"] == [{"name": "crate", "base_quantity": 30}]

    assert saved_product["selling_units"] == [
        {"name": "half crate", "base_quantity": 15}]
def test_add_product_rejects_negative_selling_price(authenticated_client):
    client, inventory_file = authenticated_client

    response = client.post("/products/add", data={"product_id": "102", "name": "Eggs", "category": "Food", "price": "100", "selling_price": "-50", "quantity": "300", "base_unit": "piece",}, follow_redirects=False,)
    assert response.status_code == 200
    assert not inventory_file.exists()

def test_add_product_rejects_non_numeric_selling_price(authenticated_client):
    client, inventory_file = authenticated_client
    response = client.post("/products/add", data={"product_id": "103", "name": "Eggs", "category": "Food", "price": "100", "selling_price": "invalid", "quantity": "300", "base_unit": "piece",},follow_redirects=False,)

    assert response.status_code == 200
    assert not inventory_file.exists()   

@pytest.fixture
def staff_client(client, tmp_path, monkeypatch):
    import web.app as web_app

    inventory_file = tmp_path / "staff_inventory.json"
    monkeypatch.setattr(web_app, "DEFAULT_INVENTORY_FILE", str(inventory_file),)

    with client.session_transaction() as session:
        session["username"] = "test_staff"
        session["role"] = "Staff"

    return client, inventory_file

@pytest.mark.parametrize("route",["/products/remove", "/products/restore", "/products/delete-permanently",],)
def test_staff_cannot_modify_product_removal_records(staff_client, route):
    client, inventory_file = staff_client

    response = client.post(route, data={"product_id": "101"}, follow_redirects=False,)

    assert response.status_code == 403
    assert not inventory_file.exists()