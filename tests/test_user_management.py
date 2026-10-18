import pytest

from web.auth import create_staff_user, load_users


def test_duplicate_username_is_rejected(tmp_path, monkeypatch):
    import json
    import web.auth as auth

    users_file = tmp_path / "users.json"
    users_file.write_text(
        json.dumps([{"username": "test_staff", "password_hash": auth.hash_password("OriginalPass123!"), "role": "Staff",}]), encoding="utf-8",)

    monkeypatch.setattr(auth, "USERS_FILE", users_file)

    with pytest.raises(ValueError, match="already exists"):
        create_staff_user("TEST_STAFF", "AnotherPass123!")

    users = load_users()
    assert len(users) == 1
    assert users[0]["username"] == "test_staff"

from web.app import app
import web.auth as auth


@pytest.fixture
def web_client():
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


def login_as_role(client, username, role):
    with client.session_transaction() as session:
        session["username"] = username
        session["role"] = role


def test_unauthenticated_user_cannot_view_staff_page(web_client):
    response = web_client.get("/staff")
    assert response.status_code == 302


def test_staff_cannot_view_staff_page(web_client):
    login_as_role(web_client, "test_staff", "Staff")

    response = web_client.get("/staff")

    assert response.status_code == 403


def test_staff_cannot_create_account(web_client):
    login_as_role(web_client, "test_staff", "Staff")

    response = web_client.post("/staff/add", data={"username": "another_staff", "password": "StrongPass123!"},)

    assert response.status_code == 403


def test_admin_can_view_staff_page_without_password_hashes(web_client, tmp_path, monkeypatch):
    users_file = tmp_path / "users.json"
    users_file.write_text(__import__("json").dumps([{"username": "admin", "password_hash": auth.hash_password("AdminTest123!"), "role": "Admin",}]), encoding="utf-8",)

    monkeypatch.setattr(auth, "USERS_FILE", users_file)
    login_as_role(web_client, "admin", "Admin")

    response = web_client.get("/staff")

    assert response.status_code == 200
    page = response.get_data(as_text=True)
    assert "admin" in page
    assert "AdminTest123!" not in page
    assert auth.load_users()[0]["password_hash"] not in page


def test_admin_can_create_staff_account(web_client, tmp_path, monkeypatch):
    users_file = tmp_path / "users.json"
    users_file.write_text(__import__("json").dumps([{"username": "admin", "password_hash": auth.hash_password("AdminTest123!"), "role": "Admin",}]), encoding="utf-8",)

    monkeypatch.setattr(auth, "USERS_FILE", users_file)
    login_as_role(web_client, "admin", "Admin")

    response = web_client.post("/staff/add", data={"username": "new_staff", "password": "StaffPass123!"}, follow_redirects=True,)

    assert response.status_code == 200

    users = auth.load_users()
    staff_user = next(user for user in users if user["username"] == "new_staff")

    assert staff_user["role"] == "Staff"
    assert staff_user["password_hash"] != "StaffPass123!"
    assert auth.verify_password("StaffPass123!", staff_user["password_hash"])

@pytest.mark.parametrize(("username", "password", "error_message"), [("ab", "StrongPass123!", "between 3 and 30 characters"), ("a" * 31, "StrongPass123!", "between 3 and 30 characters"), ("bad username", "StrongPass123!", "only letters, numbers"), ("valid_user", "short", "at least 8 characters"),],)
def test_invalid_staff_account_details_are_rejected(username, password, error_message, tmp_path, monkeypatch):
    import json
    import web.auth as auth

    users_file = tmp_path / "users.json"
    users_file.write_text("[]", encoding="utf-8")

    monkeypatch.setattr(auth, "USERS_FILE", users_file)

    with pytest.raises(ValueError, match=error_message):
        create_staff_user(username, password)

    assert json.loads(users_file.read_text(encoding="utf-8")) == []

def test_staff_username_is_trimmed(tmp_path, monkeypatch):
    import json
    import web.auth as auth

    users_file = tmp_path / "users.json"
    users_file.write_text("[]", encoding="utf-8")

    monkeypatch.setattr(auth, "USERS_FILE", users_file)

    create_staff_user("  new_staff  ", "StrongPass123!")

    users = json.loads(users_file.read_text(encoding="utf-8"))

    assert len(users) == 1
    assert users[0]["username"] == "new_staff"
    assert users[0]["role"] == "Staff"

def test_creating_staff_account_preserves_existing_admin(tmp_path, monkeypatch):
    import json
    import web.auth as auth

    users_file = tmp_path / "users.json"
    admin_hash = auth.hash_password("AdminTest123!")

    users_file.write_text(json.dumps([{"username": "admin", "password_hash": admin_hash, "role": "Admin",}]), encoding="utf-8",)

    monkeypatch.setattr(auth, "USERS_FILE", users_file)

    create_staff_user("new_staff", "StrongPass123!")

    users = auth.load_users()

    assert len(users) == 2

    admin_user = next(user for user in users if user["username"] == "admin")
    staff_user = next(user for user in users if user["username"] == "new_staff")

    assert admin_user["role"] == "Admin"
    assert admin_user["password_hash"] == admin_hash
    assert auth.verify_password("AdminTest123!", admin_user["password_hash"])

    assert staff_user["role"] == "Staff"
    assert auth.verify_password("StrongPass123!", staff_user["password_hash"])

def test_logged_out_user_cannot_view_staff_page(web_client):
    # Start with an authenticated administrator session.
    login_as_role(web_client, "admin", "Admin")

    # Log out.
    logout_response = web_client.get("/logout")
    assert logout_response.status_code == 200

    # Confirm the session no longer contains authentication details.
    with web_client.session_transaction() as session:
        assert "username" not in session
        assert "role" not in session

    # Confirm the logged-out user cannot access the staff page.
    response = web_client.get("/staff")
    assert response.status_code == 302

def test_staff_can_log_in_and_role_is_stored_in_session(web_client, tmp_path, monkeypatch):
    import json
    import web.auth as auth

    users_file = tmp_path / "users.json"
    password = "StaffPass123!"

    users_file.write_text(json.dumps([{"username": "test_staff", "password_hash": auth.hash_password(password), "role": "Staff",}]), encoding="utf-8",)

    monkeypatch.setattr(auth, "USERS_FILE", users_file)
    response = web_client.post(
        "/login",
        data={"username": "test_staff", "password": password,},)
    assert response.status_code == 302
    with web_client.session_transaction() as session:
        assert session["username"] == "test_staff"
        assert session["role"] == "Staff"

def test_staff_login_fails_with_incorrect_password(web_client, tmp_path, monkeypatch):
    import json
    import web.auth as auth

    users_file = tmp_path / "users.json"
    users_file.write_text(json.dumps([{"username": "test_staff", "password_hash": auth.hash_password("CorrectPass123!"), "role": "Staff",}]), encoding="utf-8",)

    monkeypatch.setattr(auth, "USERS_FILE", users_file)
    response = web_client.post(
        "/login",
        data={"username": "test_staff", "password": "WrongPass123!",},)
    assert response.status_code == 200
    assert response.get_data(as_text=True) == "Invalid username or password."
    with web_client.session_transaction() as session:
        assert "username" not in session
        assert "role" not in session