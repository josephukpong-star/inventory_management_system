import json

import pytest

from web.app import app


@pytest.fixture
def client():
    """Provide a Flask test client without starting the web server."""
    app.config["TESTING"] = True

    with app.test_client() as test_client:
        yield test_client


def login_as(client, username, role):
    """Create a temporary authenticated session for a route test."""
    with client.session_transaction() as session:
        session["username"] = username
        session["role"] = role


def create_test_backup(directory):
    """Create a temporary backup containing test-only data."""
    backup_data = {"products": [{"product_id": 1, "name": "Test Laptop", "category": "Electronics", "price": 500000, "quantity": 10,}], "transactions": [{"transaction_type": "STOCK-OUT", "product_name": "Test Laptop", "quantity": 2, "price": 500000, "total_value": 1000000, "sales_value": 1000000, "inventory_cost": 600000, "gross_profit": 400000,}],}
    backup_path = directory / "test_backup.json"
    backup_path.write_text(json.dumps(backup_data), encoding="utf-8",)
    return backup_path

def test_dashboard_redirects_unauthenticated_user(client):
    response = client.get("/dashboard")
    assert response.status_code == 302

def test_staff_cannot_access_financial_review(client):
    login_as(client, "test_staff", "Staff")
    response = client.get("/financial-review")
    assert response.status_code == 403

def test_staff_can_access_dashboard(client):
    login_as(client, "test_staff", "Staff")
    response = client.get("/dashboard")
    assert response.status_code == 200

def test_staff_can_access_products_page(client):
    login_as(client, "test_staff", "Staff")
    response = client.get("/products")
    assert response.status_code == 200

def test_staff_can_access_stock_page(client):
    login_as(client, "test_staff", "Staff")
    response = client.get("/stock")
    assert response.status_code == 200

def test_staff_can_access_transactions_page(client):
    login_as(client, "test_staff", "Staff")
    response = client.get("/transactions")
    assert response.status_code == 200

def test_staff_can_access_reports_page(client):
    login_as(client, "test_staff", "Staff")
    response = client.get("/reports")
    assert response.status_code == 200

def test_staff_can_access_sales_page(client):
    login_as(client, "test_staff", "Staff")
    response = client.get("/sales")
    assert response.status_code == 200

def test_staff_can_access_backups_page(client):
    login_as(client, "test_staff", "Staff")
    response = client.get("/backups")
    assert response.status_code == 200

def test_staff_cannot_access_staff_management(client):
    login_as(client, "test_staff", "Staff")
    response = client.get("/staff")
    assert response.status_code == 403

def test_staff_cannot_create_staff_account(client):
    login_as(client, "test_staff", "Staff")
    response = client.post("/staff/add", data={"username": "another_staff", "password": "SecurePass123"},)
    assert response.status_code == 403

def test_admin_can_access_staff_management(client):
    login_as(client, "test_admin", "Admin")
    response = client.get("/staff")
    assert response.status_code == 200

def test_unauthenticated_user_cannot_access_staff_management(client):
    response = client.get("/staff")
    assert response.status_code == 302

def test_staff_cannot_restore_backup(client):
    login_as(client, "test_staff", "Staff")
    response = client.post("/restore-backup", data={"backup_file": "test_backup.json"},)
    assert response.status_code == 403

def test_staff_cannot_see_financial_values_in_backup(client, tmp_path, monkeypatch):
    import web.app as web_app
    monkeypatch.setattr(web_app, "DEFAULT_BACKUP_DIRECTORY", str(tmp_path),)
    create_test_backup(tmp_path)
    login_as(client, "test_staff", "Staff")

    response = client.get("/view-backup", query_string={"backup_file": "test_backup.json"},)
    assert response.status_code == 200
    page = response.get_data(as_text=True)
    assert "Test Laptop" in page
    assert "500,000.00" not in page
    assert "1,000,000.00" not in page
    assert "400,000.00" not in page
    assert "Financial Review" not in page

def test_admin_can_see_financial_values_in_backup(client, tmp_path, monkeypatch):
    import web.app as web_app
    monkeypatch.setattr(web_app, "DEFAULT_BACKUP_DIRECTORY", str(tmp_path),)
    create_test_backup(tmp_path)
    login_as(client, "test_admin", "Admin")
    response = client.get("/view-backup", query_string={"backup_file": "test_backup.json"},)
    assert response.status_code == 200
    page = response.get_data(as_text=True)
    assert "500,000.00" in page
    assert "1,000,000.00" in page
    assert "Financial Review" in page