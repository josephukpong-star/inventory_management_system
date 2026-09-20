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
def save_inventory_data(products, transactions, file_path):
    data = {"products": [product.to_dict() for product in products], "transactions": transactions,}
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)
def save_inventory_report(report, file_path):
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(report)
def load_inventory_data(file_path):
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        return [], []
    except json.JSONDecodeError:
        return [], []
    if isinstance(data, list):
        products = [_product_from_dict(item) for item in data]  
        return products, []
    products = [_product_from_dict(item) for item in data.get("products", [])]
    transactions = data.get("transactions", [])
    return products, transactions