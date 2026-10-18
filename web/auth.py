import json
import os
import tempfile
from pathlib import Path

from werkzeug.security import generate_password_hash, check_password_hash


# Always locate users.json relative to this file, not the terminal's directory.
USERS_FILE = Path(__file__).resolve().parent / "users.json"


def hash_password(password):
    """Return a securely hashed password."""
    return generate_password_hash(password)


def verify_password(password, password_hash):
    """Check a password against its stored hash."""
    return check_password_hash(password_hash, password)


def load_users():
    """Load user accounts from the JSON file."""
    with open(USERS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_users(users):
    """Save user accounts atomically to avoid partially written JSON."""
    USERS_FILE.parent.mkdir(parents=True, exist_ok=True)

    temporary_path = None

    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=USERS_FILE.parent, suffix=".tmp", delete=False,) as file:
            temporary_path = Path(file.name)
            json.dump(users, file, indent=4)
            file.write("\n")

        os.replace(temporary_path, USERS_FILE)

    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()


def create_staff_user(username, password):
    """Create a staff account after validating its details."""
    username = (username or "").strip()

    if not 3 <= len(username) <= 30:
        raise ValueError("Username must contain between 3 and 30 characters.")

    if not all(character.isalnum() or character in "_-" for character in username):
        raise ValueError("Username may contain only letters, numbers, underscores, and hyphens.")

    if not password or len(password) < 8:
        raise ValueError("Password must contain at least 8 characters.")

    users = load_users()

    if any(user.get("username", "").casefold() == username.casefold() for user in users):
        raise ValueError("That username already exists.")

    users.append({"username": username, "password_hash": hash_password(password), "role": "Staff",})

    save_users(users)


def authenticate_user(username, password):
    """Authenticate a user without changing the existing login behavior."""
    if not username or not password:
        return None

    users = load_users()

    for user in users:
        if user["username"] == username:
            if verify_password(password, user["password_hash"]):
                return user

            return None

    return None
