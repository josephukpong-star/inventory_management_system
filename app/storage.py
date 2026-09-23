import json
from app.models import Product
def _product_from_dict(item):
    return Product(item["product_id"], item["name"], item["price"], item["quantity"], item.get("category", "Uncategorized"))
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
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)
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