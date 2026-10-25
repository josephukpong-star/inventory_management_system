import json
import os
import tempfile
from pathlib import Path
from app.models import Product


def _copy_json_file(source_file_path, destination_file_path):
    with open(source_file_path, "r") as source_file:
        data = json.load(source_file)
    with open(destination_file_path, "w") as destination_file:
        json.dump(data, destination_file, indent=4)
def _product_from_dict(item):
    return Product(item["product_id"], item["name"], item["price"], item["quantity"], item.get("category", "Uncategorized"), base_unit=item.get("base_unit", "unit"), purchase_units=item.get("purchase_units"), selling_units=item.get("selling_units"), selling_price=item.get("selling_price"),)
def save_products(products, file_path):
    data = [product.to_dict() for product in products]
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)
def load_products(file_path):
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []
    if isinstance(data, dict):
        data = data.get("products", [])
    return [_product_from_dict(item) for item in data]

def save_inventory_data(products, transactions, file_path, removed_products=None, deleted_products=None, deleted_record_counter=0,):
    data = {"products": [product.to_dict() for product in products], "transactions": transactions, "removed_products": [product.to_dict() for product in (removed_products or [])], "deleted_products": deleted_products or [], "deleted_record_counter": deleted_record_counter,}

    # Keep the temporary file in the same directory as the original.
    file_path = os.fspath(file_path)
    directory = os.path.dirname(os.path.abspath(file_path))
    filename = os.path.basename(file_path)

    temp_path = None

    try:
        # Create a temporary file in the destination directory.
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=directory, prefix=f".{filename}.", suffix=".tmp", delete=False,) as temp_file:
            temp_path = temp_file.name

            json.dump(data, temp_file, indent=4)

            # Flush Python's buffer and request that the OS flush the file.
            temp_file.flush()
            os.fsync(temp_file.fileno())

        # Replace the original only after the temporary file is complete.
        os.replace(temp_path, file_path)
        temp_path = None

    finally:
        # Clean up an incomplete temporary file if one remains.
        if temp_path is not None and os.path.exists(temp_path):
            os.remove(temp_path)

def save_inventory_report(report, file_path):
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(report)
def load_inventory_data(file_path, return_full_state=False):
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        if return_full_state:
            return [], [], [], [], 0
        return [], []
    except json.JSONDecodeError:
        if return_full_state:
            return [], [], [], [], 0
        return [], []
    if isinstance(data, list):
        products = [_product_from_dict(item) for item in data]
        if return_full_state:
            return products, [], [], [], 0
        return products, []
    products = [_product_from_dict(item) for item in data.get("products", [])]
    transactions = data.get("transactions", [])
    removed_products = [_product_from_dict(item) for item in data.get("removed_products", [])]
    deleted_products = data.get("deleted_products", [])
    deleted_record_counter = data.get("deleted_record_counter", 0)
    if return_full_state:
        return (products, transactions, removed_products, deleted_products, deleted_record_counter,)
    return products, transactions

def backup_inventory_data(source_file_path, backup_file_path):
    _copy_json_file(source_file_path, backup_file_path)

def create_inventory_backup(source_file_path, backup_directory):
    from datetime import datetime
    import os
    os.makedirs(backup_directory, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S_%f")
    backup_file_path = os.path.join(backup_directory, f"inventory_backup_{timestamp}.json",)
    backup_inventory_data(source_file_path, backup_file_path)
    return Path(backup_file_path)

def list_inventory_backups(backup_directory):
    backup_directory = Path(backup_directory)
    if not backup_directory.exists():
        return []
    return sorted(backup_directory.glob("inventory_backup_*.json"), reverse=True,)
def restore_inventory_backup(backup_file_path, source_file_path):
    backup_file_path = Path(backup_file_path)
    source_file_path = Path(source_file_path)
    if not backup_file_path.exists():
        raise FileNotFoundError(backup_file_path)
    _copy_json_file(backup_file_path, source_file_path)

def restore_inventory_data(backup_file_path, source_file_path):
    _copy_json_file(backup_file_path, source_file_path)